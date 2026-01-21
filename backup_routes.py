"""
Database Backup and Restore Routes for Web Deployment
Handles manual backup downloads and restore from uploads
"""
from flask import Blueprint, jsonify, send_file, request, session
from flask_login import login_required, current_user
from models import db, User, ExamSession, Packet, Case, Candidate, CaseImage, Question, Answer
from datetime import datetime, timedelta
import json
import io
import os

backup_bp = Blueprint('backup', __name__, url_prefix='/api/backup')

def check_admin():
    """Check if current user is admin (first registered user)"""
    try:
        if not current_user.is_authenticated:
            return False
        first_user = User.query.order_by(User.id).first()
        return first_user and current_user.id == first_user.id
    except Exception as e:
        return False

@backup_bp.route('/download', methods=['GET'])
@login_required
def download_backup():
    """Download complete database backup as JSON"""
    if not check_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    try:
        # Collect all data
        backup_data = {
            'metadata': {
                'backup_date': datetime.utcnow().isoformat(),
                'database_type': 'postgresql' if os.getenv('DATABASE_URL') else 'sqlite',
                'version': '1.0'
            },
            'users': [],
            'exam_sessions': [],
            'packets': [],
            'cases': [],
            'candidates': [],
            'case_images': [],
            'questions': [],
            'answers': []
        }
        
        # Export users (without passwords for security)
        for user in User.query.all():
            backup_data['users'].append({
                'id': user.id,
                'email': user.email,
                'full_name': user.full_name,
                'is_active': user.is_active,
                'created_at': user.created_at.isoformat() if user.created_at else None
            })
        
        # Export exam sessions
        for exam_session in ExamSession.query.all():
            backup_data['exam_sessions'].append({
                'id': exam_session.id,
                'user_id': exam_session.user_id,
                'exam_date': exam_session.exam_date.isoformat() if exam_session.exam_date else None,
                'exam_time': exam_session.exam_time,
                'session_name': exam_session.session_name,
                'created_at': exam_session.created_at.isoformat() if exam_session.created_at else None
            })
        
        # Export packets
        for packet in Packet.query.all():
            backup_data['packets'].append({
                'id': packet.id,
                'exam_id': packet.exam_id,
                'packet_number': packet.packet_number,
                'packet_id': packet.packet_id
            })
        
        # Export cases
        for case in Case.query.all():
            backup_data['cases'].append({
                'id': case.id,
                'packet_id': case.packet_id,
                'case_number': case.case_number,
                'diagnosis': case.diagnosis,
                'questions': case.questions,
                'answers': case.answers,
                'discussion': case.discussion
            })
        
        # Export candidates
        for candidate in Candidate.query.all():
            backup_data['candidates'].append({
                'id': candidate.id,
                'exam_id': candidate.exam_id,
                'candidate_name': candidate.candidate_name,
                'candidate_number': candidate.candidate_number,
                'packet_number': candidate.packet_number
            })
        
        # Export case images - prefer Cloudinary URLs, fallback to base64 for legacy
        import base64
        image_count = 0
        cloudinary_count = 0
        legacy_count = 0
        total_image_size = 0
        for image in CaseImage.query.all():
            try:
                image_data = {
                    'id': image.id,
                    'case_id': image.case_id,
                    'image_filename': image.image_filename,
                    'image_type': image.image_type,
                    'image_description': image.image_description or '',
                    'created_at': image.created_at.isoformat() if image.created_at else None
                }
                
                # Prefer Cloudinary URL (much smaller backup files)
                if image.cloudinary_url:
                    image_data['cloudinary_url'] = image.cloudinary_url
                    image_data['cloudinary_public_id'] = image.cloudinary_public_id
                    cloudinary_count += 1
                # Legacy: base64 encode if no Cloudinary URL
                elif image.image_data:
                    image_base64 = base64.b64encode(image.image_data).decode('utf-8')
                    image_size_bytes = len(image.image_data)
                    total_image_size += image_size_bytes
                    image_data['image_data'] = image_base64
                    image_data['image_size_bytes'] = image_size_bytes
                    legacy_count += 1
                else:
                    print(f"Warning: Image {image.id} has no data (neither Cloudinary nor binary), skipping...")
                    continue
                
                backup_data['case_images'].append(image_data)
                image_count += 1
            except Exception as img_error:
                print(f"Error exporting image {image.id}: {str(img_error)}")
                continue
        
        # Add image export statistics to metadata
        backup_data['metadata']['image_export_stats'] = {
            'total_images_exported': image_count,
            'cloudinary_images': cloudinary_count,
            'legacy_base64_images': legacy_count,
            'total_image_size_bytes': total_image_size,
            'total_image_size_mb': round(total_image_size / (1024 * 1024), 2)
        }
        
        # Export questions
        for question in Question.query.all():
            backup_data['questions'].append({
                'id': question.id,
                'case_id': question.case_id,
                'question_number': question.question_number,
                'question_text': question.question_text,
                'created_at': question.created_at.isoformat() if question.created_at else None
            })
        
        # Export answers
        for answer in Answer.query.all():
            backup_data['answers'].append({
                'id': answer.id,
                'case_id': answer.case_id,
                'answer_number': answer.answer_number,
                'answer_text': answer.answer_text,
                'created_at': answer.created_at.isoformat() if answer.created_at else None
            })
        
        # Create JSON file in memory
        # Use ensure_ascii=False to handle any special characters in filenames/descriptions
        try:
            json_data = json.dumps(backup_data, indent=2, ensure_ascii=False)
            json_bytes = io.BytesIO(json_data.encode('utf-8'))
            
            # Log backup statistics
            backup_size_mb = len(json_data.encode('utf-8')) / (1024 * 1024)
            print(f"Backup created: {len(backup_data.get('case_images', []))} images, {backup_size_mb:.2f} MB total")
        except Exception as json_error:
            print(f"Error creating JSON backup: {str(json_error)}")
            # Try with ASCII encoding as fallback
            json_data = json.dumps(backup_data, indent=2, ensure_ascii=True)
            json_bytes = io.BytesIO(json_data.encode('utf-8'))
        
        # Generate filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'frcr_examiner_backup_{timestamp}.json'
        
        # Update session with last backup time
        session['last_backup_time'] = datetime.utcnow().isoformat()
        
        return send_file(
            json_bytes,
            mimetype='application/json',
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Backup error: {error_details}")
        return jsonify({
            'error': f'Backup failed: {str(e)}',
            'details': error_details
        }), 500


@backup_bp.route('/verify', methods=['POST'])
@login_required
def verify_backup():
    """Verify a backup file contains all expected data including images"""
    if not check_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    if 'backup_file' not in request.files:
        return jsonify({'error': 'No backup file provided'}), 400
    
    file = request.files['backup_file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Only JSON backup files are supported'}), 400
    
    try:
        # Read and parse JSON
        backup_data = json.loads(file.read().decode('utf-8'))
        
        # Verify backup structure
        if 'metadata' not in backup_data:
            return jsonify({'error': 'Invalid backup file format'}), 400
        
        # Count items in backup
        verification = {
            'exam_sessions': len(backup_data.get('exam_sessions', [])),
            'packets': len(backup_data.get('packets', [])),
            'cases': len(backup_data.get('cases', [])),
            'candidates': len(backup_data.get('candidates', [])),
            'images': len(backup_data.get('case_images', [])),
            'questions': len(backup_data.get('questions', [])),
            'answers': len(backup_data.get('answers', []))
        }
        
        # Verify images have data
        images_with_data = 0
        images_without_data = 0
        total_image_size = 0
        
        for img in backup_data.get('case_images', []):
            if img.get('image_data') and len(img.get('image_data', '')) > 0:
                images_with_data += 1
                # Estimate size (base64 is ~33% larger than binary)
                total_image_size += len(img.get('image_data', '')) * 3 // 4
            else:
                images_without_data += 1
        
        verification['images_with_data'] = images_with_data
        verification['images_without_data'] = images_without_data
        verification['total_image_size_mb'] = round(total_image_size / (1024 * 1024), 2)
        
        # Check metadata for image stats
        if 'image_export_stats' in backup_data.get('metadata', {}):
            verification['export_stats'] = backup_data['metadata']['image_export_stats']
        
        return jsonify({
            'valid': True,
            'verification': verification,
            'message': 'Backup file verified successfully'
        })
        
    except Exception as e:
        import traceback
        return jsonify({
            'valid': False,
            'error': f'Verification failed: {str(e)}',
            'details': traceback.format_exc()
        }), 500


@backup_bp.route('/status', methods=['GET'])
@login_required
def backup_status():
    """Get backup status and reminder info"""
    if not check_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    last_backup = session.get('last_backup_time')
    
    if last_backup:
        last_backup_dt = datetime.fromisoformat(last_backup)
        hours_since = (datetime.utcnow() - last_backup_dt).total_seconds() / 3600
        needs_backup = hours_since >= 24
    else:
        needs_backup = True
        hours_since = None
    
    # Count records
    stats = {
        'total_sessions': ExamSession.query.count(),
        'total_packets': Packet.query.count(),
        'total_cases': Case.query.count(),
        'total_candidates': Candidate.query.count(),
        'total_images': CaseImage.query.count()
    }
    
    return jsonify({
        'is_admin': True,
        'last_backup_time': last_backup,
        'hours_since_backup': hours_since,
        'needs_backup': needs_backup,
        'stats': stats
    })


@backup_bp.route('/restore', methods=['POST'])
@login_required
def restore_backup():
    """Restore database from uploaded JSON backup"""
    if not check_admin():
        return jsonify({
            'error': 'Admin access required. Only the first registered user (admin) can restore backups.',
            'code': 'ADMIN_REQUIRED'
        }), 403
    
    if 'backup_file' not in request.files:
        return jsonify({'error': 'No backup file provided'}), 400
    
    file = request.files['backup_file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.json'):
        return jsonify({'error': 'Only JSON backup files are supported'}), 400
    
    try:
        # Read file content
        file_content = file.read()
        
        # Try to decode with UTF-8, fallback to other encodings if needed
        try:
            file_text = file_content.decode('utf-8')
        except UnicodeDecodeError:
            try:
                file_text = file_content.decode('utf-8-sig')  # Handle BOM
            except UnicodeDecodeError:
                try:
                    file_text = file_content.decode('latin-1')  # Fallback encoding
                except Exception as decode_error:
                    return jsonify({
                        'error': f'Failed to decode file: {str(decode_error)}. Please ensure the file is valid UTF-8 encoded JSON.'
                    }), 400
        
        # Parse JSON with better error handling
        try:
            backup_data = json.loads(file_text)
        except json.JSONDecodeError as json_error:
            return jsonify({
                'error': f'Invalid JSON format: {str(json_error)}. Please ensure the file is a valid JSON backup file.',
                'details': f'Error at line {json_error.lineno}, column {json_error.colno}'
            }), 400
        
        # Validate backup structure
        if 'metadata' not in backup_data:
            return jsonify({
                'error': 'Invalid backup file format: missing metadata. Please ensure this is a backup file exported from this application.'
            }), 400
        
        # Clear existing data (DANGEROUS - make sure user confirms)
        if not request.form.get('confirm_overwrite'):
            return jsonify({'error': 'Please confirm data overwrite'}), 400
        
        # Clear all tables (in correct order to respect foreign keys)
        Answer.query.delete()
        Question.query.delete()
        CaseImage.query.delete()
        Candidate.query.delete()
        Case.query.delete()
        Packet.query.delete()
        ExamSession.query.delete()
        # Don't delete users - keep existing users
        
        db.session.commit()
        
        # Restore exam sessions
        for session_data in backup_data.get('exam_sessions', []):
            session = ExamSession(
                id=session_data['id'],
                user_id=current_user.id,  # Assign to current user
                exam_date=datetime.fromisoformat(session_data['exam_date']) if session_data.get('exam_date') else datetime.utcnow(),
                exam_time=session_data['exam_time'],
                session_name=session_data['session_name']
            )
            db.session.add(session)
        
        db.session.flush()
        
        # Restore packets
        for packet_data in backup_data.get('packets', []):
            packet = Packet(
                id=packet_data['id'],
                exam_id=packet_data['exam_id'],
                packet_number=packet_data['packet_number'],
                packet_id=packet_data['packet_id']
            )
            db.session.add(packet)
        
        db.session.flush()
        
        # Restore cases
        for case_data in backup_data.get('cases', []):
            case = Case(
                id=case_data['id'],
                packet_id=case_data['packet_id'],
                case_number=case_data['case_number'],
                diagnosis=case_data['diagnosis'],
                questions=case_data['questions'],
                answers=case_data['answers'],
                discussion=case_data.get('discussion', '')
            )
            db.session.add(case)
        
        db.session.flush()
        
        # Restore candidates
        for candidate_data in backup_data.get('candidates', []):
            candidate = Candidate(
                id=candidate_data['id'],
                exam_id=candidate_data['exam_id'],
                candidate_name=candidate_data['candidate_name'],
                candidate_number=candidate_data['candidate_number'],
                packet_number=candidate_data['packet_number']
            )
            db.session.add(candidate)
        
        db.session.flush()
        
        # Restore case images - handle both Cloudinary URLs and legacy base64
        import base64
        restored_image_count = 0
        cloudinary_restored = 0
        legacy_restored = 0
        for image_data in backup_data.get('case_images', []):
            try:
                # Prefer Cloudinary URL (no binary data needed)
                if image_data.get('cloudinary_url'):
                    image = CaseImage(
                        id=image_data['id'],
                        case_id=image_data['case_id'],
                        cloudinary_url=image_data['cloudinary_url'],
                        cloudinary_public_id=image_data.get('cloudinary_public_id'),
                        image_filename=image_data['image_filename'],
                        image_type=image_data['image_type'],
                        image_description=image_data.get('image_description', '')
                    )
                    cloudinary_restored += 1
                # Legacy: decode base64 if no Cloudinary URL
                elif image_data.get('image_data'):
                    decoded_image_data = base64.b64decode(image_data['image_data'])
                    if len(decoded_image_data) == 0:
                        print(f"Warning: Image {image_data.get('id', 'unknown')} decoded to empty data, skipping...")
                        continue
                    
                    image = CaseImage(
                        id=image_data['id'],
                        case_id=image_data['case_id'],
                        image_data=decoded_image_data,
                        image_filename=image_data['image_filename'],
                        image_type=image_data['image_type'],
                        image_description=image_data.get('image_description', '')
                    )
                    legacy_restored += 1
                else:
                    print(f"Warning: Image {image_data.get('id', 'unknown')} has no data (neither Cloudinary nor base64), skipping...")
                    continue
                
                db.session.add(image)
                restored_image_count += 1
            except Exception as img_error:
                print(f"Error restoring image {image_data.get('id', 'unknown')}: {str(img_error)}")
                continue
        
        db.session.flush()
        
        # Restore questions
        for question_data in backup_data.get('questions', []):
            question = Question(
                id=question_data['id'],
                case_id=question_data['case_id'],
                question_number=question_data['question_number'],
                question_text=question_data['question_text']
            )
            db.session.add(question)
        
        db.session.flush()
        
        # Restore answers
        for answer_data in backup_data.get('answers', []):
            answer = Answer(
                id=answer_data['id'],
                case_id=answer_data['case_id'],
                answer_number=answer_data['answer_number'],
                answer_text=answer_data['answer_text']
            )
            db.session.add(answer)
        
        db.session.flush()
        
        # Commit all changes
        db.session.commit()
        
        # Reset sequences for PostgreSQL to avoid ID conflicts on next insert
        if 'postgresql' in str(db.engine.url):
            try:
                sequences_to_reset = [
                    'exam_session',
                    'packet', 
                    'case',
                    'candidate',
                    'case_image',
                    'question',
                    'answer'
                ]
                
                for table in sequences_to_reset:
                    try:
                        result = db.session.execute(db.text(f"SELECT MAX(id) FROM {table}"))
                        max_id = result.scalar() or 0
                        db.session.execute(db.text(f"ALTER SEQUENCE {table}_id_seq RESTART WITH {max_id + 1}"))
                    except Exception as seq_error:
                        pass
                
                db.session.commit()
            except Exception as e:
                pass
        
        # Count actually restored images
        actual_restored_images = CaseImage.query.count()
        
        return jsonify({
            'success': True,
            'message': 'Database restored successfully',
            'stats': {
                'exam_sessions': len(backup_data.get('exam_sessions', [])),
                'packets': len(backup_data.get('packets', [])),
                'cases': len(backup_data.get('cases', [])),
                'candidates': len(backup_data.get('candidates', [])),
                'images_in_backup': len(backup_data.get('case_images', [])),
                'images_restored': actual_restored_images,
                'questions': len(backup_data.get('questions', [])),
                'answers': len(backup_data.get('answers', []))
            }
        })
        
    except json.JSONDecodeError as json_error:
        db.session.rollback()
        return jsonify({
            'error': f'JSON parsing failed: {str(json_error)}',
            'details': f'Error at line {json_error.lineno}, column {json_error.colno}. Please check that the file is valid JSON.'
        }), 400
    except UnicodeDecodeError as decode_error:
        db.session.rollback()
        return jsonify({
            'error': f'File encoding error: {str(decode_error)}. Please ensure the backup file is UTF-8 encoded.'
        }), 400
    except Exception as e:
        db.session.rollback()
        import traceback
        error_details = traceback.format_exc()
        print(f"Restore error: {error_details}")
        return jsonify({
            'error': f'Restore failed: {str(e)}',
            'details': error_details if os.getenv('FLASK_ENV') == 'development' else None
        }), 500


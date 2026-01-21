"""
User authentication module
Handles login, signup, password recovery, and session management
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User
from datetime import datetime
import os
import secrets

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

def send_recovery_email(email, token):
    """
    Send password recovery email using free service
    Using Resend.com (free tier) or fallback to console for development
    """
    recovery_url = os.getenv('APP_URL', 'https://frcr-examiner.vercel.app') + url_for('auth.reset_password', token=token, _external=False)
    
    # For development, just log it
    if os.getenv('FLASK_ENV') == 'development':
        print(f"\n📧 Password Recovery Email:")
        print(f"   To: {email}")
        print(f"   Reset Link: {recovery_url}\n")
        return True
    
    # For production, use Resend (free tier: 100 emails/day)
    try:
        import requests
        resend_key = os.getenv('RESEND_API_KEY')
        
        if not resend_key:
            print(f"[EMAIL] ERROR: RESEND_API_KEY not set. Email not sent to {email}")
            print(f"[EMAIL] Recovery link (for debugging): {recovery_url}")
            return False
        
        print(f"[EMAIL] Sending recovery email to {email}")
        print(f"[EMAIL] Recovery URL: {recovery_url}")
        
        # Use onboarding@resend.dev for testing (Resend's test domain)
        # For production, replace with your verified domain
        from_email = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": from_email,
                "to": [email],
                "subject": "Reset Your FRCR Examiner Password",
                "html": f"""
                <h2>Password Reset Request</h2>
                <p>We received a request to reset your password.</p>
                <p><a href="{recovery_url}" style="background-color: #896b90; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">
                    Reset Password
                </a></p>
                <p>If you didn't request this, you can ignore this email.</p>
                <p><small>Link expires in 24 hours</small></p>
                """
            },
            timeout=10
        )
        
        print(f"[EMAIL] Response status: {response.status_code}")
        print(f"[EMAIL] Response body: {response.text}")
        
        if response.status_code != 200:
            print(f"[EMAIL] ERROR: Failed to send email. Status: {response.status_code}")
            return False
        
        print(f"[EMAIL] SUCCESS: Email sent to {email}")
        return True
        
    except Exception as e:
        print(f"[EMAIL] EXCEPTION: Error sending email: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        try:
            data = request.get_json() if request.is_json else request.form
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            full_name = data.get('full_name', '').strip()
            
            # Validation
            if not all([email, password, full_name]):
                return jsonify({'error': 'All fields required'}), 400
            
            if len(password) < 8:
                return jsonify({'error': 'Password must be at least 8 characters'}), 400
            
            # Check if user exists
            print(f"[REGISTER] Checking for existing user: {email}")
            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                print(f"[REGISTER] User already exists: {email}")
                return jsonify({'error': 'Email already registered'}), 409
            
            # Create user
            print(f"[REGISTER] Creating new user: {email}")
            user = User(email=email, full_name=full_name)
            user.set_password(password)
            
            db.session.add(user)
            print(f"[REGISTER] User added to session")
            
            db.session.commit()
            print(f"[REGISTER] User committed to database - ID: {user.id}")
            
            login_user(user)
            print(f"[REGISTER] User logged in: {email}")
            
            # Debug session creation
            from flask import session as flask_session
            print(f"[REGISTER] Session ID after login: {flask_session.get('_id', 'NO SESSION')}")
            print(f"[REGISTER] Current user authenticated: {current_user.is_authenticated}")
            
            return jsonify({'success': True, 'message': 'Registration successful'}), 201
            
        except Exception as e:
            print(f"[REGISTER] ERROR: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()
            return jsonify({'error': f'Registration failed: {str(e)}'}), 500
        
        login_user(user)
        return jsonify({'success': True, 'message': 'Registration successful'}), 201
    
    return render_template('register.html')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember = data.get('remember', False)
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if not user:
            print(f"[AUTH] User not found: {email}")
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Debug password check
        password_valid = user.check_password(password)
        print(f"[AUTH] Login attempt - Email: {email}, Password valid: {password_valid}, User active: {user.is_active}")
        
        if not password_valid:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.is_active:
            return jsonify({'error': 'Account is disabled'}), 403
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        login_user(user, remember=remember)
        
        # Debug session creation
        print(f"[AUTH] Successful login: {email}")
        print(f"[AUTH] Session created - User ID: {user.id}, Email: {user.email}")
        print(f"[AUTH] Remember: {remember}")
        
        return jsonify({'success': True, 'message': 'Login successful'}), 200
    
    return render_template('login.html')


@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """User logout"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logged out'}), 200


@auth_bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Request password recovery"""
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        email = data.get('email', '').strip().lower()
        
        if not email:
            return jsonify({'error': 'Email required'}), 400
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Generate recovery token
            token = user.generate_recovery_token()
            db.session.commit()
            
            # Send email
            email_sent = send_recovery_email(email, token)
            
            if not email_sent:
                print(f"[AUTH] Failed to send recovery email to {email}")
                return jsonify({'error': 'Failed to send recovery email. Please try again or contact support.'}), 500
        
        # Return success if user exists and email sent (don't reveal if email doesn't exist)
        return jsonify({'success': True, 'message': 'Check your email for recovery link'}), 200
    
    return render_template('forgot_password.html')


@auth_bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Reset password with token"""
    user = User.query.filter_by(recovery_token=token).first()
    
    if not user or not user.verify_recovery_token(token):
        return render_template('reset_password_expired.html'), 401
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        new_password = data.get('password', '')
        
        if not new_password or len(new_password) < 8:
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Set new password
        user.set_password(new_password)
        user.clear_recovery_token()
        db.session.commit()
        
        login_user(user)
        return jsonify({'success': True, 'message': 'Password reset successful'}), 200
    
    return render_template('reset_password.html', token=token)


@auth_bp.route('/profile', methods=['GET'])
@login_required
def profile():
    """Get current user profile"""
    # Return HTML page if requested via browser, JSON for API
    if request.headers.get('Accept') == 'application/json':
        return jsonify({
            'id': current_user.id,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'profile_pic_url': current_user.get_profile_pic_url(),
            'created_at': current_user.created_at.isoformat(),
            'last_login': current_user.last_login.isoformat() if current_user.last_login else None
        }), 200
    
    # Return HTML profile page
    return render_template('profile.html', user=current_user)


@auth_bp.route('/profile/picture', methods=['POST'])
@login_required
def upload_profile_picture():
    """Upload profile picture to Cloudinary"""
    if 'profile_pic' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['profile_pic']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    # Check file size (max 5MB for profile pics)
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        return jsonify({'error': 'File size exceeds 5MB limit'}), 400
    
    # Check file type
    import mimetypes
    allowed_types = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
    file_type = mimetypes.guess_type(file.filename)[0]
    
    if file_type not in allowed_types:
        return jsonify({'error': 'Only image files (JPEG, PNG, GIF, WebP) are allowed'}), 400
    
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Delete old profile picture from Cloudinary if exists
        if current_user.profile_pic_public_id:
            try:
                cloudinary.uploader.destroy(current_user.profile_pic_public_id)
                print(f"[CLOUDINARY] Deleted old profile pic: {current_user.profile_pic_public_id}")
            except Exception as e:
                print(f"[CLOUDINARY] Error deleting old profile pic: {e}")
        
        # Upload to Cloudinary in frcr-examiner-media/profile-pics subfolder
        upload_result = cloudinary.uploader.upload(
            file,
            folder="frcr-examiner-media/profile-pics",  # Organized under parent folder frcr-examiner-media
            resource_type="image",
            overwrite=False,
            use_filename=True,
            unique_filename=True
        )
        
        cloudinary_url = upload_result.get('secure_url')
        cloudinary_public_id = upload_result.get('public_id')
        
        print(f"[CLOUDINARY] Profile pic uploaded: {cloudinary_public_id} -> {cloudinary_url}")
        
        # Update user profile picture
        current_user.profile_pic_url = cloudinary_url
        current_user.profile_pic_public_id = cloudinary_public_id
        db.session.commit()
        
        return jsonify({
            'success': True,
            'profile_pic_url': cloudinary_url,
            'message': 'Profile picture uploaded successfully'
        })
    except Exception as e:
        db.session.rollback()
        print(f"[PROFILE] Error uploading profile picture: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Upload error: {str(e)}'}), 500


@auth_bp.route('/profile/picture', methods=['DELETE'])
@login_required
def delete_profile_picture():
    """Delete profile picture from Cloudinary"""
    try:
        import cloudinary
        import cloudinary.uploader
        
        # Delete from Cloudinary if public_id exists
        if current_user.profile_pic_public_id:
            try:
                cloudinary.uploader.destroy(current_user.profile_pic_public_id)
                print(f"[CLOUDINARY] Deleted profile pic: {current_user.profile_pic_public_id}")
            except Exception as e:
                print(f"[CLOUDINARY] Error deleting profile pic: {e}")
        
        # Clear from database
        current_user.profile_pic_url = None
        current_user.profile_pic_public_id = None
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Profile picture deleted successfully'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Delete error: {str(e)}'}), 500


@auth_bp.route('/test-email', methods=['GET'])
def test_email():
    """Test email configuration"""
    try:
        import requests
        resend_key = os.getenv('RESEND_API_KEY')
        
        result = {
            'resend_key_set': bool(resend_key),
            'resend_key_length': len(resend_key) if resend_key else 0,
            'requests_available': True,
            'app_url': os.getenv('APP_URL', 'https://frcr-examiner.vercel.app'),
            'email_from': os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
        }
        
        return jsonify(result), 200
    except ImportError as e:
        return jsonify({'error': f'Import error: {str(e)}', 'requests_available': False}), 500
    except Exception as e:
        return jsonify({'error': f'Error: {str(e)}'}), 500


@auth_bp.route('/test-send-email', methods=['GET'])
def test_send_email():
    """Actually try to send a test email and return full response"""
    try:
        import requests
        resend_key = os.getenv('RESEND_API_KEY')
        
        if not resend_key:
            return jsonify({'error': 'RESEND_API_KEY not set'}), 500
        
        from_email = os.getenv('EMAIL_FROM', 'onboarding@resend.dev')
        test_to = 'test@example.com'  # Use a test email
        
        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {resend_key}",
                "Content-Type": "application/json"
            },
            json={
                "from": from_email,
                "to": [test_to],
                "subject": "Test Email from FRCR Examiner",
                "html": "<h1>Test Email</h1><p>This is a test email.</p>"
            },
            timeout=10
        )
        
        return jsonify({
            'status_code': response.status_code,
            'response_text': response.text,
            'response_json': response.json() if response.headers.get('content-type', '').startswith('application/json') else None,
            'from_email': from_email,
            'to_email': test_to
        }), 200
        
    except Exception as e:
        import traceback
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500


@auth_bp.route('/debug', methods=['GET'])
def debug_auth():
    """Debug authentication status"""
    from flask import session
    return jsonify({
        'is_authenticated': current_user.is_authenticated,
        'user_id': current_user.id if current_user.is_authenticated else None,
        'email': current_user.email if current_user.is_authenticated else None,
        'session_id': session.get('_id', 'No session'),
        'session_keys': list(session.keys())
    }), 200


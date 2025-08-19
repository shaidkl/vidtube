from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import os
import random

app = Flask(__name__)
CORS(app)

# Database configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{os.path.join(basedir, "vidtube.db")}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads directory if it doesn't exist
if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])
if not os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')):
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails'))

db = SQLAlchemy(app)

# Database Models
class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    avatar_url = db.Column(db.String(200))
    subscribers = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    videos = db.relationship('Video', backref='channel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'avatar_url': self.avatar_url,
            'subscribers': self.subscribers,
            'subscribers_formatted': format_views(self.subscribers),
            'video_count': len(self.videos)
        }

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    thumbnail_url = db.Column(db.String(200))
    video_url = db.Column(db.String(200))
    duration = db.Column(db.String(10))
    views = db.Column(db.Integer, default=0)
    likes = db.Column(db.Integer, default=0)
    dislikes = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign key
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'video_url': self.video_url,
            'duration': self.duration,
            'views': self.views,
            'views_formatted': format_views(self.views),
            'likes': self.likes,
            'dislikes': self.dislikes,
            'category': self.category,
            'time_ago': format_time_ago(self.created_at),
            'channel': {
                'id': self.channel.id,
                'name': self.channel.name,
                'avatar_url': self.channel.avatar_url,
                'subscribers': self.channel.subscribers
            }
        }

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    avatar_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Utility functions
def format_views(views):
    """Format view count for display"""
    if views >= 1000000:
        return f"{views/1000000:.1f}M"
    elif views >= 1000:
        return f"{views/1000:.0f}K"
    return str(views)

def format_time_ago(created_at):
    """Format time ago for display"""
    now = datetime.utcnow()
    diff = now - created_at
    
    if diff.days > 365:
        years = diff.days // 365
        return f"{years} year{'s' if years > 1 else ''} ago"
    elif diff.days > 30:
        months = diff.days // 30
        return f"{months} month{'s' if months > 1 else ''} ago"
    elif diff.days > 7:
        weeks = diff.days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif diff.days > 0:
        return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return "Just now"

def init_sample_data():
    """Initialize database with sample data"""
    with app.app_context():
        db.create_all()
        
        # Check if data already exists
        if Channel.query.first():
            return
        
        print("🔄 Initializing database with sample data...")
        
        # Create sample channels
        channels_data = [
            {"name": "Nature Explorer", "subscribers": 2300000},
            {"name": "CodeMaster", "subscribers": 856000},
            {"name": "Gaming Pro", "subscribers": 1800000},
            {"name": "Culinary Arts", "subscribers": 654000},
            {"name": "Tech News Daily", "subscribers": 3100000},
            {"name": "Peaceful Sounds", "subscribers": 4200000},
            {"name": "Space Science", "subscribers": 1500000},
            {"name": "Pet Comedy", "subscribers": 5700000},
            {"name": "Fitness Plus", "subscribers": 923000},
            {"name": "Adventure Seeker", "subscribers": 678000},
            {"name": "Future Tech", "subscribers": 2800000},
            {"name": "Urban Artist", "subscribers": 445000},
        ]
        
        channels = []
        for i, channel_data in enumerate(channels_data):
            channel = Channel(
                name=channel_data["name"],
                avatar_url=f"https://picsum.photos/50/50?random={100 + i}",
                subscribers=channel_data["subscribers"]
            )
            db.session.add(channel)
            channels.append(channel)
        
        db.session.commit()
        
        # Create sample videos
        videos_data = [
            {
                "title": "Amazing Nature Documentary: Wildlife in 4K",
                "description": "Explore the stunning wildlife of our planet in breathtaking 4K resolution.",
                "duration": "15:42",
                "views": 2300000,
                "likes": 45000,
                "category": "Nature",
                "days_ago": 3,
                "thumbnail_id": 1
            },
            {
                "title": "Top 10 JavaScript Tips Every Developer Should Know",
                "description": "Essential JavaScript tips that will make you a better developer.",
                "duration": "12:15",
                "views": 856000,
                "likes": 23000,
                "category": "Technology",
                "days_ago": 7,
                "thumbnail_id": 2
            },
            {
                "title": "Epic Gaming Montage - Best Moments 2025",
                "description": "The most epic gaming moments from this year compiled into one amazing video.",
                "duration": "8:33",
                "views": 1800000,
                "likes": 67000,
                "category": "Gaming",
                "days_ago": 2,
                "thumbnail_id": 3
            },
            {
                "title": "Cooking the Perfect Pasta: Italian Chef's Secret",
                "description": "Learn the authentic Italian way to cook pasta from a master chef.",
                "duration": "18:22",
                "views": 654000,
                "likes": 18000,
                "category": "Food",
                "days_ago": 5,
                "thumbnail_id": 4
            },
            {
                "title": "Breaking: Latest Technology Trends 2025",
                "description": "Stay updated with the latest technology trends shaping our future.",
                "duration": "22:17",
                "views": 3100000,
                "likes": 89000,
                "category": "Technology",
                "days_ago": 0,
                "thumbnail_id": 5
            },
            {
                "title": "Relaxing Music for Study and Work - 2 Hours",
                "description": "Perfect background music for productivity and focus.",
                "duration": "2:15:33",
                "views": 4200000,
                "likes": 125000,
                "category": "Music",
                "days_ago": 30,
                "thumbnail_id": 6
            },
            {
                "title": "Space Exploration: Mars Mission Updates",
                "description": "Latest updates from the Mars exploration missions.",
                "duration": "25:48",
                "views": 1500000,
                "likes": 42000,
                "category": "Science",
                "days_ago": 4,
                "thumbnail_id": 7
            },
            {
                "title": "Funny Cat Compilation - Try Not to Laugh",
                "description": "The funniest cat videos that will make your day better.",
                "duration": "10:05",
                "views": 5700000,
                "likes": 234000,
                "category": "Entertainment",
                "days_ago": 14,
                "thumbnail_id": 8
            },
            {
                "title": "Workout at Home: 30 Minute Full Body",
                "description": "Complete full-body workout you can do at home with no equipment.",
                "duration": "31:42",
                "views": 923000,
                "likes": 31000,
                "category": "Fitness",
                "days_ago": 7,
                "thumbnail_id": 9
            },
            {
                "title": "Travel Vlog: Hidden Gems in Nepal",
                "description": "Discover the most beautiful hidden places in Nepal.",
                "duration": "16:28",
                "views": 678000,
                "likes": 19000,
                "category": "Travel",
                "days_ago": 21,
                "thumbnail_id": 10
            },
            {
                "title": "AI Revolution: What's Coming Next?",
                "description": "Exploring the future of artificial intelligence and its impact.",
                "duration": "19:13",
                "views": 2800000,
                "likes": 76000,
                "category": "Technology",
                "days_ago": 1,
                "thumbnail_id": 11
            },
            {
                "title": "Street Art Time-lapse: Creating a Masterpiece",
                "description": "Watch an incredible street art piece come to life in time-lapse.",
                "duration": "7:52",
                "views": 445000,
                "likes": 15000,
                "category": "Art",
                "days_ago": 5,
                "thumbnail_id": 12
            }
        ]
        
        for i, video_data in enumerate(videos_data):
            video = Video(
                title=video_data["title"],
                description=video_data["description"],
                thumbnail_url=f"https://picsum.photos/640/360?random={video_data['thumbnail_id']}",
                video_url=f"/api/videos/{i+1}/stream",
                duration=video_data["duration"],
                views=video_data["views"],
                likes=video_data["likes"],
                category=video_data["category"],
                channel_id=channels[i].id,
                created_at=datetime.utcnow() - timedelta(days=video_data["days_ago"])
            )
            db.session.add(video)
        
        db.session.commit()
        print("✅ Sample data initialized successfully!")

# API Routes
@app.route('/api/videos')
def get_videos():
    """Get all videos with optional filtering"""
    category = request.args.get('category')
    search = request.args.get('search')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 20))
    
    query = Video.query
    
    if category and category.lower() != 'all':
        query = query.filter(Video.category.ilike(f'%{category}%'))
    
    if search:
        query = query.filter(
            db.or_(
                Video.title.ilike(f'%{search}%'),
                Video.description.ilike(f'%{search}%')
            )
        )
    
    query = query.order_by(Video.created_at.desc())
    videos = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return jsonify({
        'videos': [video.to_dict() for video in videos.items],
        'total': videos.total,
        'pages': videos.pages,
        'current_page': videos.page,
        'has_next': videos.has_next,
        'has_prev': videos.has_prev
    })

@app.route('/api/videos/<int:video_id>')
def get_video(video_id):
    """Get specific video details"""
    video = Video.query.get_or_404(video_id)
    video.views += 1
    db.session.commit()
    return jsonify(video.to_dict())

@app.route('/api/videos/<int:video_id>/like', methods=['POST'])
def like_video(video_id):
    """Like a video"""
    video = Video.query.get_or_404(video_id)
    video.likes += 1
    db.session.commit()
    return jsonify({'success': True, 'likes': video.likes, 'video_id': video_id})

@app.route('/api/channels')
def get_channels():
    """Get all channels"""
    channels = Channel.query.all()
    return jsonify({'channels': [channel.to_dict() for channel in channels]})

@app.route('/api/categories')
def get_categories():
    """Get all video categories"""
    categories = db.session.query(Video.category).distinct().all()
    category_list = [cat[0] for cat in categories if cat[0]]
    return jsonify({'categories': ['All'] + sorted(category_list)})

@app.route('/api/trending')
def get_trending():
    """Get trending videos"""
    week_ago = datetime.utcnow() - timedelta(days=7)
    videos = Video.query.filter(Video.created_at >= week_ago).order_by(Video.views.desc()).limit(20).all()
    return jsonify({'videos': [video.to_dict() for video in videos]})

@app.route('/api/search')
def search_videos():
    """Search videos"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'videos': []})
    
    videos = Video.query.filter(
        db.or_(
            Video.title.ilike(f'%{query}%'),
            Video.description.ilike(f'%{query}%'),
            Video.channel.has(Channel.name.ilike(f'%{query}%'))
        )
    ).order_by(Video.views.desc()).all()
    
    return jsonify({'videos': [video.to_dict() for video in videos]})

@app.route('/api/stats')
def get_stats():
    """Get platform statistics"""
    total_videos = Video.query.count()
    total_channels = Channel.query.count()
    total_views = db.session.query(db.func.sum(Video.views)).scalar() or 0
    total_likes = db.session.query(db.func.sum(Video.likes)).scalar() or 0
    
    return jsonify({
        'total_videos': total_videos,
        'total_channels': total_channels,
        'total_views': total_views,
        'total_views_formatted': format_views(total_views),
        'total_likes': total_likes,
        'total_likes_formatted': format_views(total_likes)
    })

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'database': 'connected'
    })

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    init_sample_data()
    print("\n🚀 VidTube Backend Server Starting...")
    print("📊 Database initialized with sample data")
    print("🌐 Server running on http://localhost:5000")
    print("\n📋 Available API endpoints:")
    print("  GET  /api/videos - Get all videos")
    print("  GET  /api/videos/<id> - Get specific video")
    print("  POST /api/videos/<id>/like - Like a video")
    print("  GET  /api/channels - Get all channels")
    print("  GET  /api/trending - Get trending videos")
    print("  GET  /api/search?q=<query> - Search videos")
    print("  GET  /api/categories - Get categories")
    print("  GET  /api/stats - Get platform stats")
    print("  GET  /api/health - Health check")
    print("\n💡 Frontend should connect to: http://localhost:5000")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
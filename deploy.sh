#!/bin/bash
# Deployment script for UPAK backend

set -e

echo "🚀 Starting UPAK deployment..."

# Navigate to project directory
cd /home/upak/upak-ecosystem

# Fetch latest changes
echo "📥 Fetching latest changes..."
git fetch origin

# Checkout and merge the feature branch
echo "🔄 Merging feat/lk_endpoints..."
git checkout main
git merge origin/feat/lk_endpoints

# Install new dependencies
echo "📦 Installing dependencies..."
pip3 install --user PyJWT==2.8.0 bcrypt==4.1.2

# Initialize database
echo "🗄️ Initializing database..."
python3 init_db.py

# Restart the service
echo "🔄 Restarting UPAK service..."
sudo systemctl restart upak.service

# Check service status
echo "✅ Checking service status..."
sudo systemctl status upak.service --no-pager

echo "✨ Deployment completed successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Test the endpoints: python3 test_endpoints.py"
echo "2. Check logs: sudo journalctl -u upak.service -f"
echo ""
echo "🔗 PR Link: https://github.com/Yuriuser1/upak-ecosystem/pull/3"

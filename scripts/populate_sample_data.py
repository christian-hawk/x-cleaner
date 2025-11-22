"""
Populate database with sample data for testing the Streamlit dashboard.

This script creates realistic sample data to test the dashboard without
requiring actual X API credentials or a real scan.
"""

import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.database import DatabaseManager
from backend.models import CategorizedAccount

# Sample categories with characteristics
CATEGORIES = {
    "AI/ML Researchers & Practitioners": {
        "keywords": ["AI", "ML", "Deep Learning", "Neural Networks", "Research"],
        "verified_rate": 0.7,
        "avg_followers": 50000,
        "count": 85
    },
    "Tech Entrepreneurs & Founders": {
        "keywords": ["Founder", "CEO", "Startup", "Tech", "Innovation"],
        "verified_rate": 0.6,
        "avg_followers": 80000,
        "count": 72
    },
    "Software Engineers & Developers": {
        "keywords": ["Developer", "Engineer", "Programming", "Code", "Software"],
        "verified_rate": 0.3,
        "avg_followers": 15000,
        "count": 120
    },
    "Data Scientists & Analysts": {
        "keywords": ["Data Science", "Analytics", "Statistics", "Python", "Data"],
        "verified_rate": 0.4,
        "avg_followers": 20000,
        "count": 68
    },
    "Tech News & Media": {
        "keywords": ["Tech News", "Journalist", "Reporter", "Media", "Technology"],
        "verified_rate": 0.9,
        "avg_followers": 150000,
        "count": 45
    },
    "Product Managers & Designers": {
        "keywords": ["Product", "Design", "UX", "UI", "Manager"],
        "verified_rate": 0.5,
        "avg_followers": 25000,
        "count": 58
    },
    "Open Source Contributors": {
        "keywords": ["Open Source", "OSS", "Contributor", "GitHub", "Developer"],
        "verified_rate": 0.2,
        "avg_followers": 12000,
        "count": 92
    },
    "DevOps & Cloud Engineers": {
        "keywords": ["DevOps", "Cloud", "AWS", "Kubernetes", "Infrastructure"],
        "verified_rate": 0.35,
        "avg_followers": 18000,
        "count": 54
    },
    "Venture Capitalists & Investors": {
        "keywords": ["VC", "Investor", "Venture Capital", "Funding", "Investment"],
        "verified_rate": 0.8,
        "avg_followers": 120000,
        "count": 38
    },
    "Cybersecurity Experts": {
        "keywords": ["Security", "Cybersecurity", "Hacker", "InfoSec", "Privacy"],
        "verified_rate": 0.6,
        "avg_followers": 35000,
        "count": 42
    },
    "Tech Podcasters & YouTubers": {
        "keywords": ["Podcast", "YouTuber", "Content Creator", "Tech", "Video"],
        "verified_rate": 0.7,
        "avg_followers": 95000,
        "count": 36
    },
    "Academic Researchers": {
        "keywords": ["Professor", "PhD", "Research", "University", "Academic"],
        "verified_rate": 0.5,
        "avg_followers": 28000,
        "count": 48
    },
    "Blockchain & Crypto": {
        "keywords": ["Blockchain", "Crypto", "Bitcoin", "Ethereum", "Web3"],
        "verified_rate": 0.4,
        "avg_followers": 45000,
        "count": 62
    },
    "Tech Community Leaders": {
        "keywords": ["Community", "Organizer", "Meetup", "Conference", "Leader"],
        "verified_rate": 0.45,
        "avg_followers": 22000,
        "count": 51
    },
    "Tech Writers & Authors": {
        "keywords": ["Writer", "Author", "Book", "Technical Writing", "Content"],
        "verified_rate": 0.55,
        "avg_followers": 32000,
        "count": 44
    }
}


def generate_sample_accounts():
    """Generate realistic sample accounts."""
    accounts = []
    user_id_counter = 1000000

    for category, info in CATEGORIES.items():
        for i in range(info["count"]):  # type: ignore[arg-type]
            user_id_counter += 1

            # Generate username
            username = f"user_{category.replace(' ', '_').lower()}_{i+1}"[:50]

            # Generate display name
            display_name = f"{random.choice(['John', 'Jane', 'Alex', 'Sam', 'Chris', 'Taylor'])} {random.choice(['Smith', 'Johnson', 'Williams', 'Brown', 'Davis', 'Miller'])}"

            # Generate bio
            keyword: str = random.choice(info["keywords"])  # type: ignore[arg-type]
            bio = f"{keyword} enthusiast | Sharing insights about {keyword.lower()} | Building the future"

            # Determine if verified
            verified = random.random() < info["verified_rate"]  # type: ignore[operator]

            # Generate follower count (log-normal distribution)
            followers_base = info["avg_followers"]
            followers_count = int(random.lognormvariate(
                random.uniform(8, 12),
                random.uniform(0.8, 1.5)
            ))
            followers_count = max(100, min(followers_count, followers_base * 5))  # type: ignore[operator]

            # Following count (inversely related to followers for influencers)
            following_count = int(random.uniform(100, 2000))
            if followers_count > 100000:
                following_count = int(random.uniform(100, 500))

            # Tweet count (related to account age and activity)
            tweet_count = int(random.uniform(100, 50000))

            # Location
            locations = ["San Francisco, CA", "New York, NY", "London, UK", "Berlin, Germany",
                        "Tokyo, Japan", "Singapore", "Austin, TX", "Seattle, WA", None]
            location = random.choice(locations)

            # Website
            website = f"https://{username.replace('_', '')}.com" if random.random() < 0.4 else None

            # Confidence score (higher for verified, established accounts)
            confidence = random.uniform(0.75, 0.99) if verified else random.uniform(0.65, 0.90)

            # Reasoning
            reasoning = f"Categorized as '{category}' based on bio keywords ('{keyword}'), account activity patterns, and follower demographics. High confidence due to clear professional focus."

            # Created at (random date in past 5 years)
            days_ago = random.randint(30, 1825)
            created_at = datetime.now() - timedelta(days=days_ago)

            # Analyzed at (recent)
            analyzed_at = datetime.now() - timedelta(hours=random.randint(1, 48))

            account = CategorizedAccount(
                user_id=str(user_id_counter),
                username=username,
                display_name=display_name,
                bio=bio,
                verified=verified,
                created_at=created_at,
                followers_count=followers_count,
                following_count=following_count,
                tweet_count=tweet_count,
                location=location,
                website=website,
                profile_image_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={username}",
                category=category,
                confidence=confidence,
                reasoning=reasoning,
                analyzed_at=analyzed_at
            )

            accounts.append(account)

    return accounts


def main():
    """Main function to populate database."""
    print("🔄 Generating sample data...")

    # Generate accounts
    accounts = generate_sample_accounts()

    print(f"✅ Generated {len(accounts)} sample accounts")
    print(f"📁 Categories: {len(CATEGORIES)}")

    # Initialize database
    print("\n🗄️ Initializing database...")
    db = DatabaseManager()

    # Save categories metadata
    print("💾 Saving category metadata...")
    categories_data = {
        "categories": [
            {
                "name": name,
                "description": f"Accounts focused on {name.lower()}",
                "characteristics": info["keywords"],
                "estimated_percentage": (info["count"] / len(accounts)) * 100 if accounts else 0  # type: ignore[operator]
            }
            for name, info in CATEGORIES.items()
        ]
    }
    db.save_categories(categories_data)

    # Save accounts
    print("💾 Saving accounts to database...")
    db.save_accounts(accounts)

    print("\n✅ Database populated successfully!")
    print(f"\n📊 Summary:")
    print(f"  • Total Accounts: {len(accounts)}")
    print(f"  • Categories: {len(CATEGORIES)}")
    print(f"  • Verified Accounts: {sum(1 for acc in accounts if acc.verified)}")
    print(f"  • Database: {db.db_path}")

    print("\n🚀 You can now run the Streamlit dashboard:")
    print("   streamlit run streamlit_app/app.py")


if __name__ == "__main__":
    main()

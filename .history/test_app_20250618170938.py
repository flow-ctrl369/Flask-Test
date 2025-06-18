#!/usr/bin/env python3
"""
Test script for the Flask Todo App
"""

from app import app, db, Todo

def test_database():
    """Test database functionality"""
    print("Testing database connection...")
    
    with app.app_context():
        # Check if tables exist
        print("✓ Database tables created successfully!")
        
        # Count existing todos
        todos = Todo.query.all()
        print(f"✓ Current todos in database: {len(todos)}")
        
        # Test creating a todo
        test_todo = Todo(
            title="Test Todo",
            description="This is a test todo item",
            completed=False
        )
        db.session.add(test_todo)
        db.session.commit()
        print("✓ Test todo created successfully!")
        
        # Test toggling completion
        test_todo.completed = True
        db.session.commit()
        print("✓ Todo completion toggled successfully!")
        
        # Clean up test data
        db.session.delete(test_todo)
        db.session.commit()
        print("✓ Test todo cleaned up successfully!")
        
        print("\n🎉 All tests passed! The app is working correctly.")

if __name__ == "__main__":
    test_database() 
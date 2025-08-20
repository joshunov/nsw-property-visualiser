#!/usr/bin/env python3
"""
Eastern Suburbs Property AI Chatbot Runner
Command-line interface for the AI-powered property chatbot
"""

import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Try to import AI chatbot first, fall back to basic if needed
try:
    from chatbot.ai_chatbot import AIChatbot
    AI_AVAILABLE = True
except ImportError:
    AI_AVAILABLE = False
    print("⚠️  AI chatbot not available, using basic chatbot")

from chatbot.property_chatbot import PropertyChatbot

def main():
    """Main function to run the chatbot"""
    print("🤖 AI-Powered Eastern Suburbs Property Chatbot")
    print("=" * 60)
    print("This chatbot uses OpenAI ChatGPT API for intelligent responses!")
    print("Ask me anything about Eastern Suburbs property data!")
    print("Type 'quit' to exit, 'suggestions' for example questions.")
    print("Type 'web' to start the web interface.")
    print("Type 'cache' to manage cache settings.")
    print("Type 'ai' to switch to AI mode (default).")
    print("Type 'basic' to switch to basic mode.\n")
    
    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        print("⚠️  Warning: OPENAI_API_KEY not found in environment variables.")
        print("   The AI chatbot requires an OpenAI API key to function.")
        print("   Set it with: export OPENAI_API_KEY='your-api-key-here'")
        print("   Or pass it as a parameter when initializing the chatbot.\n")
    
    # Initialize chatbot with cache
    print("🔄 Loading data and initializing AI...")
    try:
        if AI_AVAILABLE:
            chatbot = AIChatbot(use_cache=True)
            print("✅ AI chatbot initialized successfully!")
        else:
            chatbot = PropertyChatbot(use_cache=True)
            print("✅ Basic chatbot initialized successfully!")
    except Exception as e:
        print(f"❌ Failed to initialize AI chatbot: {e}")
        print("Falling back to basic chatbot...")
        try:
            chatbot = PropertyChatbot(use_cache=True)
            print("✅ Basic chatbot initialized successfully!")
        except Exception as e2:
            print(f"❌ Failed to initialize basic chatbot: {e2}")
            return
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for using the Property Chatbot!")
                break
            
            elif user_input.lower() == 'suggestions':
                print("\n💡 Here are some example questions you can ask:")
                suggestions = chatbot.get_suggestions()
                for i, suggestion in enumerate(suggestions, 1):
                    print(f"  {i}. {suggestion}")
                print()
            
            elif user_input.lower() == 'web':
                try:
                    from chatbot.web_interface import app
                    print("🌐 Starting web interface...")
                    print("Open your browser and go to: http://localhost:5000")
                    app.run(debug=False, host='0.0.0.0', port=5000)
                except ImportError:
                    print("❌ Flask not installed. Install with: pip install flask")
                break
            
            elif user_input.lower() == 'cache':
                print("\n🗂️ Cache Management Options:")
                print("1. Check cache status")
                print("2. Build/refresh cache")
                print("3. Clear cache")
                print("4. Test performance")
                print("5. Back to chatbot")
                
                cache_choice = input("\nEnter choice (1-5): ").strip()
                
                if cache_choice == '1':
                    print("\n🔍 Checking cache status...")
                    try:
                        from manage_chatbot_cache import check_cache
                        check_cache()
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                elif cache_choice == '2':
                    print("\n🏗️ Building/refreshing cache...")
                    try:
                        from manage_chatbot_cache import build_cache
                        build_cache()
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                elif cache_choice == '3':
                    print("\n🗑️ Clearing cache...")
                    try:
                        from manage_chatbot_cache import clear_cache
                        clear_cache()
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                elif cache_choice == '4':
                    print("\n⚡ Testing performance...")
                    try:
                        from manage_chatbot_cache import test_performance
                        test_performance()
                    except Exception as e:
                        print(f"❌ Error: {e}")
                
                elif cache_choice == '5':
                    print("Returning to chatbot...")
                
                else:
                    print("Invalid choice. Returning to chatbot...")
                
                print()
                continue
            
            elif user_input.lower() == 'ai':
                print("🤖 Switching to AI mode...")
                try:
                    if AI_AVAILABLE:
                        chatbot = AIChatbot(use_cache=True)
                        print("✅ AI chatbot activated!")
                    else:
                        print("❌ AI chatbot not available")
                except Exception as e:
                    print(f"❌ Failed to switch to AI mode: {e}")
                continue
            
            elif user_input.lower() == 'basic':
                print("🔧 Switching to basic mode...")
                try:
                    chatbot = PropertyChatbot(use_cache=True)
                    print("✅ Basic chatbot activated!")
                except Exception as e:
                    print(f"❌ Failed to switch to basic mode: {e}")
                continue
            
            elif not user_input:
                continue
            
            # Process query
            print("🤖 AI is thinking...")
            response = chatbot.process_query(user_input)
            print(f"\n🤖 **AI Chatbot:**\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using the AI Property Chatbot!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()

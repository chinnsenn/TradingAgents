#!/usr/bin/env python3
"""
Launch script for TradingAgents Gradio GUI
"""

import os
import sys
import argparse
import subprocess
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_dependencies():
    """Check if required dependencies are installed."""
    required_packages = [
        'gradio',
        'langchain',
        'langchain-openai',
        'langgraph',
        'pandas',
        'yfinance',
        'finnhub-python',
        'praw',
        'stockstats'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"❌ Missing required packages: {', '.join(missing_packages)}")
        print("Please install missing packages with:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_environment():
    """Check if required environment variables are set."""
    required_env_vars = [
        'FINNHUB_API_KEY'
    ]
    
    missing_vars = []
    
    for var in required_env_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("Please set the following environment variables:")
        for var in missing_vars:
            print(f"export {var}=your_api_key_here")
        print("\nYou can still run the GUI, but some features may not work properly.")
        return False
    
    return True

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="Launch TradingAgents Gradio GUI",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        '--host',
        default='0.0.0.0',
        help='Host to bind the server to'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=7860,
        help='Port to run the server on'
    )
    
    parser.add_argument(
        '--share',
        action='store_true',
        help='Create a public shareable link'
    )
    
    parser.add_argument(
        '--auth',
        help='Authentication in format "username:password"'
    )
    
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug mode'
    )
    
    parser.add_argument(
        '--no-check-deps',
        action='store_true',
        help='Skip dependency check'
    )
    
    parser.add_argument(
        '--no-check-env',
        action='store_true',
        help='Skip environment variable check'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print("=" * 60)
    print("🚀 TradingAgents Gradio GUI Launcher")
    print("=" * 60)
    print()
    
    # Check dependencies
    if not args.no_check_deps:
        print("🔍 Checking dependencies...")
        if not check_dependencies():
            sys.exit(1)
        print("✅ Dependencies OK")
        print()
    
    # Check environment
    if not args.no_check_env:
        print("🔍 Checking environment...")
        env_ok = check_environment()
        if env_ok:
            print("✅ Environment OK")
        print()
    
    # Import and launch the app
    try:
        print("🔧 Importing TradingAgents...")
        from gradio_app import create_interface
        
        print("🎛️  Creating interface...")
        demo = create_interface()
        
        # Parse authentication if provided
        auth = None
        if args.auth:
            if ':' in args.auth:
                username, password = args.auth.split(':', 1)
                auth = (username, password)
            else:
                print("❌ Invalid auth format. Use username:password")
                sys.exit(1)
        
        # Launch configuration
        print("🚀 Launching Gradio interface...")
        print(f"   Host: {args.host}")
        print(f"   Port: {args.port}")
        print(f"   Share: {'Yes' if args.share else 'No'}")
        print(f"   Auth: {'Yes' if auth else 'No'}")
        print(f"   Debug: {'Yes' if args.debug else 'No'}")
        print()
        
        if not args.share:
            print(f"🌐 Access the GUI at: http://{args.host}:{args.port}")
        
        print("=" * 60)
        print("🎉 TradingAgents GUI is ready!")
        print("=" * 60)
        
        # Launch the interface
        demo.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            auth=auth,
            show_error=args.debug,
            debug=args.debug,
            quiet=not args.debug
        )
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down...")
        sys.exit(0)
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the TradingAgents directory and all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        if args.debug:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
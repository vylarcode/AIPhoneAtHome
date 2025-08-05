#!/usr/bin/env python3
"""
Health check and testing script for Phone AI Agent
"""
import asyncio
import aiohttp
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

async def check_api_health():
    """Check API health endpoint"""
    print("Checking API health...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print("✅ API is running")
                    print(f"   Status: {data.get('status')}")
                    print(f"   Whisper: {data.get('checks', {}).get('whisper')}")
                    print(f"   Ollama: {data.get('checks', {}).get('ollama')}")
                    print(f"   TTS: {data.get('checks', {}).get('tts')}")
                    return True
                else:
                    print(f"❌ API returned status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Failed to connect to API: {e}")
        return False

async def check_ollama():
    """Check Ollama connection"""
    print("\nChecking Ollama...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:11434/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    print("✅ Ollama is running")
                    print(f"   Available models: {', '.join(models)}")
                    return True
                else:
                    print(f"❌ Ollama returned status {response.status}")
                    return False
    except Exception as e:
        print(f"❌ Failed to connect to Ollama: {e}")
        print("   Make sure Ollama is running: ollama serve")
        return False

async def test_websocket():
    """Test WebSocket connection"""
    print("\nTesting WebSocket...")
    try:
        import websockets
        uri = "ws://localhost:8000/media-stream"
        
        async with websockets.connect(uri) as websocket:
            print("✅ WebSocket connected")
            
            # Send test message
            test_msg = '{"event": "connected"}'
            await websocket.send(test_msg)
            print("   Sent test message")
            
            # Close connection
            await websocket.close()
            return True
            
    except Exception as e:
        print(f"❌ WebSocket test failed: {e}")
        return False

async def main():
    """Run all health checks"""
    print("=" * 50)
    print("Phone AI Agent Health Check")
    print("=" * 50)
    
    results = []
    
    # Run checks
    results.append(await check_api_health())
    results.append(await check_ollama())
    results.append(await test_websocket())
    
    print("\n" + "=" * 50)
    print("Health Check Summary")
    print("=" * 50)
    
    if all(results):
        print("✅ All systems operational!")
        print("\nYou can now:")
        print("1. Configure Twilio webhook to point to your public URL")
        print("2. Start ngrok: ngrok http 8000")
        print("3. Update PUBLIC_URL in .env with ngrok URL")
        print("4. Make a test call to your Twilio number")
    else:
        print("⚠️ Some checks failed. Please fix the issues above.")

if __name__ == "__main__":
    asyncio.run(main())

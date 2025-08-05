#!/usr/bin/env python3
"""
Download and install required models
"""
import os
import sys
import subprocess
import urllib.request
from pathlib import Path

def download_file(url, destination):
    """Download a file with progress"""
    def download_progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        percent = min(downloaded * 100 / total_size, 100)
        print(f"Downloading: {percent:.1f}%", end='\r')
    
    urllib.request.urlretrieve(url, destination, download_progress)
    print()

def install_whisper_models():
    """Install Whisper models"""
    print("\nInstalling Whisper models...")
    
    try:
        # Import to trigger download
        from faster_whisper import WhisperModel
        
        models = ["tiny", "base", "small"]
        models_dir = Path("./models/whisper")
        models_dir.mkdir(parents=True, exist_ok=True)
        
        for model_name in models:
            print(f"Downloading {model_name} model...")
            model = WhisperModel(model_name, device="cpu", download_root=str(models_dir))
            print(f"✅ {model_name} model ready")
            
        return True
        
    except Exception as e:
        print(f"❌ Failed to install Whisper models: {e}")
        return False

def install_piper_models():
    """Install Piper TTS models"""
    print("\nInstalling Piper TTS models...")
    
    models_dir = Path("./models/piper")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Piper model URLs (example - update with actual URLs)
    models = {
        "en_US-amy-medium": {
            "onnx": "https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx",
            "json": "https://github.com/rhasspy/piper/releases/download/v1.2.0/en_US-amy-medium.onnx.json"
        }
    }
    
    print("⚠️ Piper models need to be downloaded manually from:")
    print("   https://github.com/rhasspy/piper/releases")
    print(f"   Place them in: {models_dir}")
    
    # Create placeholder
    readme_path = models_dir / "README.txt"
    readme_path.write_text(
        "Download Piper models from:\n"
        "https://github.com/rhasspy/piper/releases\n\n"
        "Required files:\n"
        "- en_US-amy-medium.onnx\n"
        "- en_US-amy-medium.onnx.json\n"
    )
    
    return True

def install_ollama_models():
    """Install Ollama models"""
    print("\nInstalling Ollama models...")
    
    try:
        # Check if Ollama is running
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            print("⚠️ Ollama not running. Start it with: ollama serve")
            return False
            
        # Pull recommended models
        models = ["llama3.2", "mistral"]
        
        for model in models:
            print(f"Pulling {model}...")
            result = subprocess.run(
                ["ollama", "pull", model],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print(f"✅ {model} installed")
            else:
                print(f"⚠️ Failed to pull {model}")
                
        return True
        
    except FileNotFoundError:
        print("❌ Ollama not found. Install from: https://ollama.ai")
        return False
    except Exception as e:
        print(f"❌ Failed to install Ollama models: {e}")
        return False

def main():
    """Install all models"""
    print("=" * 50)
    print("Model Installation")
    print("=" * 50)
    
    results = []
    
    # Install models
    results.append(install_whisper_models())
    results.append(install_piper_models())
    results.append(install_ollama_models())
    
    print("\n" + "=" * 50)
    print("Installation Summary")
    print("=" * 50)
    
    if all(results):
        print("✅ All models installed successfully!")
    else:
        print("⚠️ Some models need manual installation")
        print("\nManual steps:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Download Piper models: https://github.com/rhasspy/piper/releases")
        print("3. Run: ollama pull llama3.2")

if __name__ == "__main__":
    main()

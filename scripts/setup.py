#!/usr/bin/env python3
"""
Setup script for Phone AI Agent
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path
import argparse

class SetupManager:
    """Manage setup and installation"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.os_type = platform.system().lower()
        self.python_version = sys.version_info
        
    def check_python(self):
        """Check Python version"""
        print("Checking Python version...")
        if self.python_version < (3, 10):
            print(f"❌ Python 3.10+ required. Found: {sys.version}")
            return False
        print(f"✅ Python {sys.version} OK")
        return True
        
    def check_cuda(self):
        """Check CUDA availability"""
        print("Checking CUDA...")
        try:
            import torch
            if torch.cuda.is_available():
                print(f"✅ CUDA available: {torch.cuda.get_device_name(0)}")
                return True
            else:
                print("⚠️ CUDA not available, will use CPU (slower)")
                return False
        except ImportError:
            print("⚠️ PyTorch not installed yet")
            return False
    
    def install_dependencies(self):
        """Install Python dependencies"""
        print("\nInstalling Python dependencies...")
        requirements_file = self.base_dir.parent / "requirements.txt"
        
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
            ], check=True)
            print("✅ Dependencies installed")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install dependencies: {e}")
            return False
            
    def setup_ollama(self):
        """Setup Ollama"""
        print("\nSetting up Ollama...")
        
        # Check if Ollama is installed
        if shutil.which("ollama"):
            print("✅ Ollama found")
            
            # Pull default model
            print("Pulling default model (llama3.2)...")
            try:
                subprocess.run(["ollama", "pull", "llama3.2"], check=True)
                print("✅ Model downloaded")
                return True
            except subprocess.CalledProcessError:
                print("⚠️ Failed to pull model, please run: ollama pull llama3.2")
                return False
        else:
            print("❌ Ollama not found. Please install from https://ollama.ai")
            return False
    
    def setup_models_directory(self):
        """Create models directory"""
        print("\nSetting up models directory...")
        models_dir = self.base_dir.parent / "models"
        models_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (models_dir / "whisper").mkdir(exist_ok=True)
        (models_dir / "piper").mkdir(exist_ok=True)
        
        print("✅ Models directory created")
        return True
        
    def setup_environment(self):
        """Setup environment file"""
        print("\nSetting up environment...")
        env_example = self.base_dir.parent / "config" / ".env.example"
        env_file = self.base_dir.parent / ".env"
        
        if not env_file.exists():
            shutil.copy(env_example, env_file)
            print("✅ Created .env file from template")
            print("⚠️ Please edit .env file with your Twilio credentials")
        else:
            print("✅ .env file already exists")
            
        return True
        
    def test_setup(self):
        """Test the setup"""
        print("\nTesting setup...")
        
        # Test imports
        try:
            import fastapi
            import whisper
            import twilio
            print("✅ Core imports successful")
            return True
        except ImportError as e:
            print(f"❌ Import error: {e}")
            return False
            
    def run(self):
        """Run complete setup"""
        print("=" * 50)
        print("Phone AI Agent Setup")
        print("=" * 50)
        
        steps = [
            ("Python version", self.check_python),
            ("CUDA support", self.check_cuda),
            ("Dependencies", self.install_dependencies),
            ("Ollama", self.setup_ollama),
            ("Models directory", self.setup_models_directory),
            ("Environment", self.setup_environment),
            ("Test imports", self.test_setup)
        ]
        
        results = []
        for name, func in steps:
            print(f"\n{name}...")
            results.append(func())
            
        print("\n" + "=" * 50)
        print("Setup Summary:")
        print("=" * 50)
        
        for (name, _), result in zip(steps, results):
            status = "✅" if result else "❌"
            print(f"{status} {name}")
            
        if all(results):
            print("\n🎉 Setup complete! You can now run the application.")
            print("\nNext steps:")
            print("1. Edit .env file with your Twilio credentials")
            print("2. Install ngrok: https://ngrok.com/download")
            print("3. Run: python app/main.py")
        else:
            print("\n⚠️ Setup incomplete. Please fix the errors above.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup Phone AI Agent")
    parser.add_argument("--skip-cuda", action="store_true", help="Skip CUDA check")
    args = parser.parse_args()
    
    setup = SetupManager()
    setup.run()

"""
Metrics collection for monitoring and performance tracking
"""
from prometheus_client import Counter, Histogram, Gauge, generate_latest
import time
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MetricsCollector:
    """Collect and expose application metrics"""
    
    def __init__(self):
        # Call metrics
        self.calls_total = Counter('calls_total', 'Total number of calls')
        self.calls_active = Gauge('calls_active', 'Number of active calls')
        self.calls_failed = Counter('calls_failed', 'Number of failed calls')
        
        # Latency metrics
        self.stt_latency = Histogram('stt_latency_ms', 'Speech-to-text latency in milliseconds')
        self.llm_latency = Histogram('llm_latency_ms', 'LLM response latency in milliseconds')
        self.tts_latency = Histogram('tts_latency_ms', 'Text-to-speech latency in milliseconds')
        self.first_response_latency = Histogram('first_response_latency_ms', 'Time to first response')
        
        # Audio metrics
        self.audio_chunks_processed = Counter('audio_chunks_processed', 'Total audio chunks processed')
        self.vad_detections = Counter('vad_detections', 'Voice activity detections')
        self.interruptions = Counter('interruptions', 'User interruptions detected')
        
        # Error metrics
        self.stt_errors = Counter('stt_errors', 'Speech-to-text errors')
        self.llm_errors = Counter('llm_errors', 'LLM generation errors')
        self.tts_errors = Counter('tts_errors', 'Text-to-speech errors')
        
        # Call tracking
        self.call_start_times: Dict[str, float] = {}
    
    def record_call_start(self, call_sid: str):
        """Record call start"""
        self.calls_total.inc()
        self.calls_active.inc()
        self.call_start_times[call_sid] = time.time()
        logger.info(f"Call started: {call_sid}")
        
    def record_call_end(self, call_sid: str):
        """Record call end"""
        self.calls_active.dec()
        
        if call_sid in self.call_start_times:
            duration = time.time() - self.call_start_times[call_sid]
            del self.call_start_times[call_sid]
            logger.info(f"Call ended: {call_sid}, duration: {duration:.2f}s")
            
    def record_stt_latency(self, latency_ms: float):
        """Record STT latency"""
        self.stt_latency.observe(latency_ms)
        
    def record_llm_latency(self, latency_ms: float):
        """Record LLM latency"""
        self.llm_latency.observe(latency_ms)
        
    def record_tts_latency(self, latency_ms: float):
        """Record TTS latency"""
        self.tts_latency.observe(latency_ms)
        
    def record_first_response(self, latency_ms: float):
        """Record first response time"""
        self.first_response_latency.observe(latency_ms)
        
    def record_interruption(self):
        """Record user interruption"""
        self.interruptions.inc()
        
    def record_error(self, error_type: str):
        """Record error by type"""
        if error_type == "stt":
            self.stt_errors.inc()
        elif error_type == "llm":
            self.llm_errors.inc()
        elif error_type == "tts":
            self.tts_errors.inc()
            
    def get_metrics(self) -> bytes:
        """Get Prometheus metrics"""
        return generate_latest()
        
    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary"""
        return {
            'active_calls': self.calls_active._value.get(),
            'total_calls': self.calls_total._value.get(),
            'failed_calls': self.calls_failed._value.get(),
            'interruptions': self.interruptions._value.get()
        }

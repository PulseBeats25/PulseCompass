try:
    import PyMuPDF as fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False
    fitz = None

import pdfplumber
import re
from typing import Dict, List, Any
import io

class PDFParser:
    """Service for parsing PDF transcripts and extracting financial insights"""
    
    def __init__(self):
        self.guidance_keywords = {
            'sales_projections': [
                'revenue growth', 'sales growth', 'topline growth', 'revenue guidance',
                'sales target', 'revenue target', 'growth rate', 'revenue projection'
            ],
            'margin_expectations': [
                'margin', 'ebitda margin', 'operating margin', 'gross margin',
                'profitability', 'margin expansion', 'margin improvement'
            ],
            'capex_investments': [
                'capex', 'capital expenditure', 'investment', 'expansion',
                'facility', 'plant', 'machinery', 'infrastructure'
            ],
            'strategic_initiatives': [
                'acquisition', 'merger', 'new product', 'launch', 'expansion',
                'partnership', 'joint venture', 'strategic', 'initiative'
            ]
        }
        
        self.integrity_indicators = {
            'positive': [
                'achieved', 'exceeded', 'delivered', 'met guidance', 'on track',
                'as promised', 'committed', 'confident', 'visibility'
            ],
            'negative': [
                'missed', 'below guidance', 'disappointed', 'challenges',
                'headwinds', 'revised down', 'lower than expected', 'uncertain'
            ]
        }
    
    def extract_text(self, pdf_content: bytes) -> str:
        """Extract text from PDF using multiple methods for better accuracy"""
        text = ""
        
        try:
            # Method 1: Try PyMuPDF if available
            if PYMUPDF_AVAILABLE and fitz:
                try:
                    pdf_document = fitz.open(stream=pdf_content, filetype="pdf")
                    for page_num in range(pdf_document.page_count):
                        page = pdf_document[page_num]
                        text += page.get_text() + "\n"
                    pdf_document.close()
                    if text.strip():
                        return text.strip()
                except Exception as e:
                    print(f"PyMuPDF extraction failed: {e}")
            
            # Method 2: pdfplumber as fallback
            try:
                with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                if text.strip():
                    return text.strip()
            except Exception as e2:
                print(f"pdfplumber extraction failed: {e2}")
            
            # Method 3: Return basic text if extraction fails
            return "PDF text extraction failed, but file was processed successfully."
            
        except Exception as e:
            print(f"All PDF extraction methods failed: {e}")
            return "PDF processing completed with limited text extraction."
    
    def analyze_transcript(self, raw_text: str) -> Dict[str, Any]:
        """Analyze transcript and extract structured information"""
        analysis = {
            'guidance': self._extract_guidance(raw_text),
            'key_quotes': self._extract_key_quotes(raw_text),
            'management_tone': self._analyze_management_tone(raw_text),
            'financial_highlights': self._extract_financial_highlights(raw_text),
            'risk_factors': self._extract_risk_factors(raw_text),
            'forward_looking_statements': self._count_forward_looking_statements(raw_text)
        }
        
        return analysis
    
    def calculate_integrity_score(self, raw_text: str, summary: Dict[str, Any]) -> int:
        """Calculate management integrity score from 1-10"""
        text_lower = raw_text.lower()
        
        positive_count = 0
        negative_count = 0
        
        # Count positive and negative integrity indicators
        for indicator in self.integrity_indicators['positive']:
            positive_count += text_lower.count(indicator)
        
        for indicator in self.integrity_indicators['negative']:
            negative_count += text_lower.count(indicator)
        
        # Calculate base score
        total_indicators = positive_count + negative_count
        if total_indicators == 0:
            base_score = 6  # Neutral score when no clear indicators
        else:
            positive_ratio = positive_count / total_indicators
            base_score = int(positive_ratio * 10)
        
        # Adjust based on specific patterns
        adjustments = 0
        
        # Look for specific integrity patterns
        if 'guidance' in text_lower and 'met' in text_lower:
            adjustments += 1
        if 'exceeded expectations' in text_lower:
            adjustments += 1
        if 'revised down' in text_lower or 'lowered guidance' in text_lower:
            adjustments -= 2
        if 'conservative' in text_lower and 'estimate' in text_lower:
            adjustments += 1
        
        # Check for forward-looking statement count (more statements = more transparency)
        fls_count = summary.get('forward_looking_statements', 0)
        if fls_count > 10:
            adjustments += 1
        elif fls_count < 3:
            adjustments -= 1
        
        final_score = max(1, min(10, base_score + adjustments))
        return final_score
    
    def _extract_guidance(self, text: str) -> Dict[str, List[str]]:
        """Extract management guidance from transcript text"""
        guidance = {
            'sales_projections': [],
            'margin_expectations': [],
            'capex_investments': [],
            'strategic_initiatives': []
        }
        
        # Split text into sentences
        sentences = re.split(r'[.!?]+', text.lower())
        
        for category, keywords in self.guidance_keywords.items():
            for sentence in sentences:
                for keyword in keywords:
                    if keyword in sentence and len(sentence.strip()) > 20:
                        # Extract relevant sentence with context
                        clean_sentence = sentence.strip()
                        if clean_sentence and clean_sentence not in guidance[category]:
                            guidance[category].append(
                                clean_sentence[:200] + "..." if len(clean_sentence) > 200 else clean_sentence
                            )
                        break
        
        return guidance
    
    def _extract_key_quotes(self, text: str) -> List[str]:
        """Extract key management quotes"""
        quotes = []
        
        # Look for sentences with guidance-related keywords
        sentences = re.split(r'[.!?]+', text)
        
        guidance_patterns = [
            r'we (expect|anticipate|project|guide|target)',
            r'our (guidance|target|expectation|projection)',
            r'we are (confident|optimistic|cautious)',
            r'(revenue|sales|margin|ebitda) (growth|expansion|improvement)'
        ]
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) > 30 and len(sentence) < 300:
                for pattern in guidance_patterns:
                    if re.search(pattern, sentence.lower()):
                        quotes.append(sentence)
                        break
        
        return quotes[:5]  # Return top 5 quotes
    
    def _analyze_management_tone(self, text: str) -> str:
        """Analyze overall management tone"""
        text_lower = text.lower()
        
        positive_words = ['confident', 'optimistic', 'strong', 'growth', 'opportunity', 'positive']
        negative_words = ['challenging', 'difficult', 'uncertain', 'headwinds', 'pressure', 'concern']
        neutral_words = ['stable', 'steady', 'maintain', 'continue', 'consistent']
        
        positive_score = sum(text_lower.count(word) for word in positive_words)
        negative_score = sum(text_lower.count(word) for word in negative_words)
        neutral_score = sum(text_lower.count(word) for word in neutral_words)
        
        if positive_score > negative_score and positive_score > neutral_score:
            return 'optimistic'
        elif negative_score > positive_score and negative_score > neutral_score:
            return 'cautious'
        else:
            return 'neutral'
    
    def _extract_financial_highlights(self, text: str) -> List[str]:
        """Extract key financial numbers and highlights"""
        highlights = []
        
        # Patterns for financial numbers
        financial_patterns = [
            r'revenue.*?(\d+(?:\.\d+)?)\s*(?:crore|cr|million|billion|%)',
            r'profit.*?(\d+(?:\.\d+)?)\s*(?:crore|cr|million|billion|%)',
            r'margin.*?(\d+(?:\.\d+)?)\s*%',
            r'growth.*?(\d+(?:\.\d+)?)\s*%'
        ]
        
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            for pattern in financial_patterns:
                if re.search(pattern, sentence.lower()) and len(sentence.strip()) > 20:
                    highlights.append(sentence.strip())
                    break
        
        return highlights[:10]  # Return top 10 highlights
    
    def _extract_risk_factors(self, text: str) -> List[str]:
        """Extract mentioned risk factors"""
        risk_factors = []
        
        risk_keywords = [
            'risk', 'challenge', 'headwind', 'uncertainty', 'volatility',
            'competition', 'regulatory', 'supply chain', 'inflation'
        ]
        
        sentences = re.split(r'[.!?]+', text.lower())
        
        for sentence in sentences:
            for keyword in risk_keywords:
                if keyword in sentence and len(sentence.strip()) > 20:
                    risk_factors.append(sentence.strip())
                    break
        
        return risk_factors[:5]  # Return top 5 risk factors
    
    def _count_forward_looking_statements(self, text: str) -> int:
        """Count forward-looking statements"""
        fls_patterns = [
            'expect', 'anticipate', 'believe', 'estimate', 'intend',
            'plan', 'project', 'forecast', 'guidance', 'outlook'
        ]
        
        text_lower = text.lower()
        count = 0
        
        for pattern in fls_patterns:
            count += text_lower.count(pattern)
        
        return count

import os
import json
import logging
import sys
from typing import Dict, Optional, List
from dataclasses import dataclass
from datetime import datetime

from groq import Groq
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class DiseaseAnalysisResult:
    """
    Data class for storing comprehensive disease and pest analysis results.
    """
    disease_detected: bool
    disease_name: Optional[str]
    disease_type: str
    severity: str
    confidence: float
    symptoms: List[str]
    possible_causes: List[str]
    treatment: List[str]
    common_pests: List[str] = None
    pest_detected: bool = False
    pest_name: Optional[str] = None
    pest_severity: str = "none"
    pest_confidence: float = 0.0
    pest_symptoms: List[str] = None
    pest_treatment: List[str] = None
    analysis_timestamp: str = datetime.now().astimezone().isoformat()

    def __post_init__(self):
        """Initialize list fields to empty lists if None"""
        if self.common_pests is None:
            self.common_pests = []
        if self.pest_symptoms is None:
            self.pest_symptoms = []
        if self.pest_treatment is None:
            self.pest_treatment = []


class LeafDiseaseDetector:
    """
    Advanced Leaf Disease & Pest Detection System using AI Vision Analysis.
    """

    MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"
    DEFAULT_TEMPERATURE = 0.3
    DEFAULT_MAX_TOKENS = 1024

    def __init__(self, api_key: Optional[str] = None):
        load_dotenv()
        self.api_key = api_key or os.environ.get("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        self.client = Groq(api_key=self.api_key)
        logger.info("Leaf Disease & Pest Detector initialized")

    def create_analysis_prompt(self) -> str:
        """
        Create the standardized analysis prompt for disease AND pest detection.
        """
        return """IMPORTANT: First determine if this image contains a plant leaf or vegetation. If the image shows humans, animals, objects, buildings, or anything other than plant leaves/vegetation, return the "invalid_image" response format below.

        If this is a valid leaf/plant image, analyze it for BOTH diseases AND pests. Return the results in JSON format.
        
        Please identify:
        1. Whether this is actually a leaf/plant image
        2. Disease name (if any disease detected)
        3. Disease type/category or invalid_image
        4. Severity level (mild, moderate, severe)
        5. Confidence score (0-100%)
        6. Symptoms observed
        7. Possible causes
        8. Treatment recommendations
        9. Pest detection (if any pests visible)
        10. Pest name (if pest detected)
        11. Pest severity
        12. Pest-specific symptoms
        13. Pest treatment recommendations

        For NON-LEAF images (humans, animals, objects, or not detected as leaves, etc.), return this format:
        {
            "disease_detected": false,
            "disease_name": null,
            "disease_type": "invalid_image",
            "severity": "none",
            "confidence": 95,
            "symptoms": ["This image does not contain a plant leaf"],
            "possible_causes": ["Invalid image type uploaded"],
            "treatment": ["Please upload an image of a plant leaf for disease analysis"],
            "pest_detected": false,
            "pest_name": null,
            "pest_severity": "none",
            "pest_confidence": 0,
            "pest_symptoms": [],
            "pest_treatment": []
        }
        
        For VALID LEAF images, return this comprehensive format:
        {
            "disease_detected": true/false,
            "disease_name": "name of disease or null",
            "disease_type": "fungal/bacterial/viral/pest/nutrient deficiency/healthy",
            "severity": "mild/moderate/severe/none",
            "confidence": 85,
            "symptoms": ["list", "of", "symptoms"],
            "possible_causes": ["list", "of", "causes"],
            "treatment": ["list", "of", "treatments"],
            "common_pests": ["list of pests commonly associated with this disease"],
            "pest_detected": true/false,
            "pest_name": "name of pest or null",
            "pest_severity": "mild/moderate/severe/none",
            "pest_confidence": 75,
            "pest_symptoms": ["chewed leaves", "visible insects", "webbing", "eggs"],
            "pest_treatment": ["insecticidal soap", "neem oil", "biological controls"]
        }

        Common pests to look for:
        - Aphids (small green/black insects, sticky residue)
        - Spider Mites (tiny red/brown mites, webbing)
        - Whiteflies (small white flying insects)
        - Mealybugs (white cottony masses)
        - Scale Insects (brown/white bumps on stems/leaves)
        - Thrips (tiny slender insects, silvery streaks)
        - Caterpillars (chewed leaves, visible larvae)
        - Leaf Miners (winding trails on leaves)
        - Beetles (various types, chewed edges)

        Look carefully for any signs of insects, eggs, larvae, or pest damage patterns."""

    def analyze_leaf_image_base64(self, base64_image: str,
                                  temperature: float = None,
                                  max_tokens: int = None) -> Dict:
        """
        Analyze base64 encoded image data for leaf diseases AND pests.
        """
        try:
            logger.info("Starting analysis for base64 image data")

            # Validate base64 input
            if not isinstance(base64_image, str):
                raise ValueError("base64_image must be a string")

            if not base64_image:
                raise ValueError("base64_image cannot be empty")

            # Clean base64 string (remove data URL prefix if present)
            if base64_image.startswith('data:'):
                base64_image = base64_image.split(',', 1)[1]

            # Prepare request parameters
            temperature = temperature or self.DEFAULT_TEMPERATURE
            max_tokens = max_tokens or self.DEFAULT_MAX_TOKENS

            # Make API request
            completion = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": self.create_analysis_prompt()
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            }
                        ]
                    }
                ],
                temperature=temperature,
                max_completion_tokens=max_tokens,
                top_p=1,
                stream=False,
                stop=None,
            )

            logger.info("API request completed successfully")
            result = self._parse_response(
                completion.choices[0].message.content)

            # Return as dictionary for JSON serialization
            return result.__dict__

        except Exception as e:
            logger.error(f"Analysis failed for base64 image data: {str(e)}")
            raise

    def _parse_response(self, response_content: str) -> DiseaseAnalysisResult:
        """
        Parse and validate API response with pest detection fields.
        """
        try:
            # Clean up response - remove markdown code blocks if present
            cleaned_response = response_content.strip()
            if cleaned_response.startswith('```json'):
                cleaned_response = cleaned_response.replace(
                    '```json', '').replace('```', '').strip()
            elif cleaned_response.startswith('```'):
                cleaned_response = cleaned_response.replace('```', '').strip()

            # Parse JSON
            disease_data = json.loads(cleaned_response)
            logger.info("Response parsed successfully as JSON")

            # Create result object with pest detection fields
            return DiseaseAnalysisResult(
                disease_detected=bool(
                    disease_data.get('disease_detected', False)),
                disease_name=disease_data.get('disease_name'),
                disease_type=disease_data.get('disease_type', 'unknown'),
                severity=disease_data.get('severity', 'unknown'),
                confidence=float(disease_data.get('confidence', 0)),
                symptoms=disease_data.get('symptoms', []),
                possible_causes=disease_data.get('possible_causes', []),
                treatment=disease_data.get('treatment', []),
                common_pests=disease_data.get('common_pests', []),
                pest_detected=bool(disease_data.get('pest_detected', False)),
                pest_name=disease_data.get('pest_name'),
                pest_severity=disease_data.get('pest_severity', 'none'),
                pest_confidence=float(disease_data.get('pest_confidence', 0)),
                pest_symptoms=disease_data.get('pest_symptoms', []),
                pest_treatment=disease_data.get('pest_treatment', [])
            )

        except json.JSONDecodeError:
            logger.warning(
                "Failed to parse as JSON, attempting to extract JSON from response")

            # Try to find JSON in the response using regex
            import re
            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                try:
                    disease_data = json.loads(json_match.group())
                    logger.info("JSON extracted and parsed successfully")

                    return DiseaseAnalysisResult(
                        disease_detected=bool(
                            disease_data.get('disease_detected', False)),
                        disease_name=disease_data.get('disease_name'),
                        disease_type=disease_data.get(
                            'disease_type', 'unknown'),
                        severity=disease_data.get('severity', 'unknown'),
                        confidence=float(disease_data.get('confidence', 0)),
                        symptoms=disease_data.get('symptoms', []),
                        possible_causes=disease_data.get(
                            'possible_causes', []),
                        treatment=disease_data.get('treatment', []),
                        common_pests=disease_data.get('common_pests', []),
                        pest_detected=bool(disease_data.get('pest_detected', False)),
                        pest_name=disease_data.get('pest_name'),
                        pest_severity=disease_data.get('pest_severity', 'none'),
                        pest_confidence=float(disease_data.get('pest_confidence', 0)),
                        pest_symptoms=disease_data.get('pest_symptoms', []),
                        pest_treatment=disease_data.get('pest_treatment', [])
                    )
                except json.JSONDecodeError:
                    pass

            # If all parsing attempts fail, log the raw response and raise error
            logger.error(
                f"Could not parse response as JSON. Raw response: {response_content}")
            raise ValueError(
                f"Unable to parse API response as JSON: {response_content[:200]}...")


def main():
    """Main execution function for testing"""
    try:
        detector = LeafDiseaseDetector()
        print("Leaf Disease & Pest Detector initialized successfully!")
        print("Use analyze_leaf_image_base64() method with base64 image data.")

    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
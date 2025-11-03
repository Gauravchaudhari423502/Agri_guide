from django.conf import settings
import logging

# Try to import Google Generative AI; fall back gracefully if unavailable
try:
    import google.generativeai as genai  # type: ignore
    _GENAI_AVAILABLE = True
except Exception:
    genai = None  # type: ignore
    _GENAI_AVAILABLE = False

logger = logging.getLogger(__name__)

# Initialize the Gemini API with the provided key (from settings)
API_KEY = getattr(settings, "GEMINI_API_KEY", None)
if _GENAI_AVAILABLE and API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        logger.warning("Failed to configure Gemini API: %s", e)
        _GENAI_AVAILABLE = False

# Prepare model (choose a fast, general model)
_MODEL = None
if _GENAI_AVAILABLE:
    try:
        # Prefer newer model if available, fallback to gemini-pro
        for model_name in [
            "gemini-1.5-flash",
            "gemini-pro"
        ]:
            try:
                _MODEL = genai.GenerativeModel(model_name)
                break
            except Exception:
                continue
        if _MODEL is None:
            _GENAI_AVAILABLE = False
    except Exception as e:
        logger.warning("Failed to initialize Gemini model: %s", e)
        _GENAI_AVAILABLE = False

def get_agriculture_response(user_message, language="en"):
    """
    Get a response from Gemini API focused on agriculture topics.
    
    Args:
        user_message (str): The user's message/question
        language (str): The language code for the response (default: "en")
    
    Returns:
        str: The AI-generated response
    """
    try:
        # If Gemini is available, call it
        if _GENAI_AVAILABLE and _MODEL is not None:
            # Enhanced system prompt for better agriculture responses
            system_prompt = f"""You are AgriBot, an expert agricultural assistant with deep knowledge in:

AGRICULTURE EXPERTISE:
- Crop selection and cultivation techniques
- Soil health, testing, and improvement strategies
- Irrigation systems and water management
- Pest and disease identification and control
- Fertilizer application and nutrient management
- Weather patterns and climate adaptation
- Sustainable farming practices
- Organic farming methods
- Crop rotation and intercropping
- Harvest timing and post-harvest handling
- Farm equipment and technology
- Market analysis and crop economics

RESPONSE GUIDELINES:
- Provide specific, actionable advice
- Include relevant technical details when helpful
- Suggest practical solutions for common farming problems
- Mention safety considerations for chemical applications
- Consider environmental sustainability in recommendations
- Be encouraging and supportive to farmers
- If asked about non-agricultural topics, politely redirect to farming

LANGUAGE: {language if language != 'en' else 'English'}"""

            try:
                chat = _MODEL.start_chat(history=[])
                response = chat.send_message(
                    f"{system_prompt}\n\nUser Question: {user_message}\n\nPlease provide a comprehensive, helpful response about this agricultural topic:"
                )
                text = getattr(response, "text", None) or ""
                if text.strip():
                    logger.info("Gemini API response received successfully")
                    return text.strip()
            except Exception as api_error:
                logger.warning(f"Gemini API call failed: {api_error}")
                # Fall through to fallback

        # Enhanced fallback responses
        user_lower = user_message.lower()
        
        # More comprehensive keyword matching
        if any(word in user_lower for word in ['crop', 'plant', 'seed', 'cultivation']):
            return """🌱 **Crop Selection & Cultivation**

For successful crop selection, consider these key factors:

**Soil Requirements:**
- Test soil pH (6.0-7.0 ideal for most crops)
- Check nutrient levels (N-P-K ratios)
- Assess drainage and water retention

**Climate Considerations:**
- Temperature ranges and frost dates
- Rainfall patterns and seasonal variations
- Humidity and wind conditions

**Popular Crop Options:**
- **Grains:** Rice, wheat, corn, barley
- **Vegetables:** Tomatoes, peppers, leafy greens
- **Legumes:** Beans, peas, lentils
- **Root crops:** Potatoes, carrots, onions

**Best Practices:**
- Start with soil preparation and testing
- Choose disease-resistant varieties
- Plan crop rotation to maintain soil health
- Consider intercropping for space efficiency

Would you like specific advice for your region or soil type?"""

        elif any(word in user_lower for word in ['soil', 'fertility', 'nutrient', 'ph']):
            return """🌍 **Soil Health & Management**

Healthy soil is the foundation of successful farming:

**Soil Testing:**
- Test pH levels (6.0-7.0 optimal for most crops)
- Check macronutrients: Nitrogen (N), Phosphorus (P), Potassium (K)
- Assess micronutrients: Iron, Zinc, Manganese
- Test organic matter content (aim for 3-5%)

**Improving Soil Health:**
- Add organic matter (compost, manure)
- Practice crop rotation
- Use cover crops (clover, rye, vetch)
- Minimize tillage to preserve structure
- Apply lime to raise pH if needed

**Nutrient Management:**
- Use balanced fertilizers (N-P-K ratios)
- Consider organic options (compost, bone meal)
- Apply nutrients based on soil test results
- Time applications for maximum efficiency

**Common Issues:**
- **Low pH:** Add agricultural lime
- **Poor drainage:** Improve with organic matter
- **Compaction:** Reduce tillage, add organic matter

Need help with specific soil problems?"""

        elif any(word in user_lower for word in ['water', 'irrigation', 'drainage']):
            return """💧 **Water Management & Irrigation**

Efficient water use is crucial for sustainable farming:

**Irrigation Systems:**
- **Drip irrigation:** Most efficient, reduces water waste
- **Sprinkler systems:** Good for large areas
- **Flood irrigation:** Traditional but less efficient
- **Rainwater harvesting:** Sustainable water source

**Water Conservation:**
- Mulch around plants to retain moisture
- Use drought-resistant crop varieties
- Implement proper drainage systems
- Monitor soil moisture levels

**Best Practices:**
- Water early morning or evening
- Avoid overwatering (check soil moisture)
- Group plants by water needs
- Use timers for consistent watering

**Signs of Water Stress:**
- Wilting leaves
- Stunted growth
- Yellowing foliage
- Poor fruit development

Need specific irrigation advice for your crops?"""

        elif any(word in user_lower for word in ['pest', 'disease', 'insect', 'fungus']):
            return """🐛 **Pest & Disease Management**

Integrated Pest Management (IPM) approach:

**Prevention Strategies:**
- Choose disease-resistant varieties
- Practice crop rotation
- Maintain proper spacing
- Keep fields clean of debris
- Monitor regularly for early detection

**Natural Control Methods:**
- Beneficial insects (ladybugs, lacewings)
- Companion planting (marigolds, basil)
- Physical barriers (row covers, traps)
- Biological controls (Bacillus thuringiensis)

**Common Pests & Solutions:**
- **Aphids:** Spray with soapy water, introduce ladybugs
- **Caterpillars:** Use Bt (Bacillus thuringiensis)
- **Fungal diseases:** Improve air circulation, avoid overhead watering
- **Weeds:** Mulch, hand-pull, use cover crops

**Chemical Controls (use as last resort):**
- Always follow label instructions
- Use appropriate protective equipment
- Apply during recommended times
- Consider environmental impact

Need help identifying specific pests or diseases?"""

        elif any(word in user_lower for word in ['fertilizer', 'nutrient', 'compost', 'manure']):
            return """🌿 **Fertilizer & Nutrient Management**

Proper nutrition is essential for healthy crops:

**Types of Fertilizers:**
- **Organic:** Compost, manure, bone meal, fish emulsion
- **Synthetic:** NPK fertilizers, micronutrient supplements
- **Slow-release:** Provides nutrients over time
- **Liquid:** Quick absorption, good for foliar feeding

**Nutrient Requirements:**
- **Nitrogen (N):** Promotes leafy growth
- **Phosphorus (P):** Root development, flowering
- **Potassium (K):** Disease resistance, fruit quality
- **Micronutrients:** Iron, zinc, manganese, boron

**Application Methods:**
- **Broadcast:** Spread evenly over soil surface
- **Side-dressing:** Apply near plant roots
- **Foliar feeding:** Spray on leaves
- **Injection:** Direct application to root zone

**Timing Considerations:**
- Apply based on crop growth stages
- Consider weather conditions
- Follow soil test recommendations
- Avoid over-application

**Organic Options:**
- Compost: Improves soil structure and nutrients
- Manure: Rich in nitrogen, improves soil health
- Cover crops: Green manure for soil improvement
- Mulching: Retains moisture, adds organic matter

Need specific fertilizer recommendations for your crops?"""

        else:
            return """🌾 **Welcome to AgriBot - Your Agriculture Assistant!**

I'm here to help with all your farming questions. I can assist with:

**🌱 Crop Management:**
- Crop selection and planning
- Planting techniques and timing
- Growth monitoring and care

**🌍 Soil Health:**
- Soil testing and analysis
- Nutrient management
- pH adjustment and fertility

**💧 Water Management:**
- Irrigation planning and systems
- Water conservation techniques
- Drainage solutions

**🐛 Pest & Disease Control:**
- Identification and prevention
- Natural and chemical treatments
- Integrated pest management

**🌿 Fertilizer & Nutrition:**
- Nutrient requirements
- Application methods
- Organic and synthetic options

**🌱 Sustainable Practices:**
- Organic farming methods
- Crop rotation strategies
- Environmental conservation

**What specific agricultural topic would you like help with today?**"""

    except Exception as e:
        logger.error(f"Error in get_agriculture_response: {e}")
        return f"I'm sorry, I encountered an error processing your request. Please try again or contact support if the issue persists."

def get_crop_recommendation(soil_data):
    """
    Get crop recommendations based on soil and weather data.
    
    Args:
        soil_data (dict): Dictionary containing soil and weather parameters
    
    Returns:
        dict: Recommended crop and description
    """
    try:
        # Simple crop recommendation logic based on soil parameters
        nitrogen = float(soil_data.get('nitrogen', 0))
        phosphorus = float(soil_data.get('phosphorus', 0))
        potassium = float(soil_data.get('potassium', 0))
        temperature = float(soil_data.get('temperature', 25))
        humidity = float(soil_data.get('humidity', 50))
        ph = float(soil_data.get('ph', 7))
        rainfall = float(soil_data.get('rainfall', 100))
        
        # Simple recommendation logic
        if temperature > 25 and humidity > 60 and rainfall > 150:
            return {
                "crop": "Rice",
                "description": "Rice is suitable for your conditions with high temperature, humidity, and rainfall. It thrives in warm, wet environments."
            }
        elif temperature < 20 and ph > 6.5:
            return {
                "crop": "Wheat",
                "description": "Wheat is suitable for cooler temperatures and slightly alkaline soil. Wheat grows well in temperate climates."
            }
        elif nitrogen > 50 and phosphorus > 30:
            return {
                "crop": "Corn",
                "description": "Corn is ideal for your soil with high nitrogen and phosphorus content. It's a heavy feeder that benefits from rich soil."
            }
        elif temperature > 20 and ph < 7:
            return {
                "crop": "Tomatoes",
                "description": "Tomatoes are perfect for your warm climate and slightly acidic soil. They require good drainage and regular watering."
            }
        else:
            return {
                "crop": "Mixed Vegetables",
                "description": "Based on your soil conditions, a mix of vegetables like beans, peas, and leafy greens would be suitable. Consider soil amendments for optimal growth."
            }
            
    except Exception as e:
        # Return a fallback recommendation in case of API errors
        return {
            "crop": "Unable to determine",
            "description": f"Could not process the data at this time. Error: {str(e)}"
        }
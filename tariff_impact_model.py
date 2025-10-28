import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import google.generativeai as genai
from prophet import Prophet
import logging
import json
import os

# Configure Gemini API with safety settings and API version
GEMINI_API_KEY = 'AIzaSyBUNRjNbCKTmWuSrCYs9WiuT_U8z0SXs5M'

# Configure the client
genai.configure(
    api_key=GEMINI_API_KEY,
    transport='rest'  # Explicitly set transport to REST
)

# Safety settings
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]

# Generation config
generation_config = {
    "temperature": 0.3,  # Reduced for more focused responses
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 2048,  # Increased token limit
    "stop_sequences": [],
    "candidate_count": 1,
}

# Initialize the model with all configurations
model = genai.GenerativeModel(
    model_name='gemini-2.5-pro',  # Using Gemini 2.5 Pro
    generation_config=generation_config,
    safety_settings=safety_settings
)

class TariffImpactModel:
    def __init__(self):
        self.df = pd.read_csv("large_dataset.csv")
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.model = None
        
    def analyze_tariff_impact(self, product_id, tariff_percentage, category=None):
        """Analyze the impact of tariffs on specific products or categories"""
        
        # Get product/category details
        if product_id:
            product_data = self.df[self.df['product_id'] == product_id]
            if product_data.empty:
                return {"error": "Product ID not found"}
            category = product_data['category'].iloc[0] if category is None else category
            
        # Generate Gemini API prompt
        prompt = f"""Analyze {tariff_percentage}% tariff impact on {category}:
1. Supply chain effects
2. Price impact
3. Mitigation strategies
4. Demand changes
Provide brief, actionable insights."""
        
        try:
            # Get analysis from Gemini with proper error handling and debug info
            response = model.generate_content(
                prompt,
                safety_settings=safety_settings,
                generation_config=generation_config
            )
            
            # Print debug information
            print(f"Response received: {response}")
            
            # Check finish reason first
            if not response.candidates or response.candidates[0].finish_reason == "MAX_TOKENS":
                # If we hit token limit, try again with a shorter prompt
                prompt = f"Brief impact analysis of {tariff_percentage}% tariff on {category} products."
                response = model.generate_content(
                    prompt,
                    safety_settings=safety_settings,
                    generation_config=generation_config
                )
            
            try:
                if hasattr(response, 'text'):
                    tariff_analysis = response.text
                else:
                    # Handle structured response
                    candidate = response.candidates[0]
                    if hasattr(candidate.content, 'text'):
                        tariff_analysis = candidate.content.text
                    elif hasattr(candidate.content, 'parts') and candidate.content.parts:
                        tariff_analysis = candidate.content.parts[0].text
                    else:
                        return {
                            "error": "No content in response",
                            "details": "Response lacks expected content structure",
                            "response_debug": str(response)
                        }
            except Exception as e:
                return {
                    "error": "Failed to extract analysis content",
                    "details": str(e),
                    "response_debug": str(response)
                }
            
            # Calculate financial impact
            if product_id:
                recent_data = self.df[self.df['product_id'] == product_id].tail(30)
                avg_price = recent_data['price'].mean()
                avg_sales = recent_data['sales'].mean()
                
                # Calculate impact metrics
                price_impact = avg_price * (1 + tariff_percentage/100)
                estimated_demand_change = -0.5 * (tariff_percentage/100)  # Simple price elasticity model
                projected_sales = avg_sales * (1 + estimated_demand_change)
                
                # Generate recommendations
                if estimated_demand_change < -0.2:  # 20% demand drop threshold
                    stock_recommendation = "REDUCE_INVENTORY"
                    warning_level = "HIGH"
                elif estimated_demand_change < -0.1:  # 10% demand drop threshold
                    stock_recommendation = "MAINTAIN_CAUTIOUS"
                    warning_level = "MEDIUM"
                else:
                    stock_recommendation = "MAINTAIN_NORMAL"
                    warning_level = "LOW"
                
                return {
                    "product_id": product_id,
                    "category": category,
                    "tariff_percentage": tariff_percentage,
                    "current_metrics": {
                        "average_price": round(avg_price, 2),
                        "average_sales": round(avg_sales, 2)
                    },
                    "projected_impact": {
                        "estimated_new_price": round(price_impact, 2),
                        "estimated_sales_change": f"{estimated_demand_change*100:.1f}%",
                        "projected_daily_sales": round(projected_sales, 2)
                    },
                    "recommendations": {
                        "warning_level": warning_level,
                        "stock_strategy": stock_recommendation,
                        "ai_analysis": tariff_analysis,
                        "action_items": self._generate_action_items(warning_level, estimated_demand_change, tariff_percentage)
                    }
                }
            else:
                # Category-level analysis
                category_data = self.df[self.df['category'] == category]
                if category_data.empty:
                    return {"error": "Category not found"}
                
                # Aggregate category metrics
                avg_category_impact = {
                    "category": category,
                    "tariff_percentage": tariff_percentage,
                    "market_analysis": tariff_analysis,
                    "affected_products": len(category_data['product_id'].unique()),
                    "average_category_price": round(category_data['price'].mean(), 2),
                    "recommendations": self._analyze_category_impact(category_data, tariff_percentage)
                }
                
                return avg_category_impact
                
        except Exception as e:
            print(f"Error during analysis generation: {str(e)}")
            return {
                "error": "Analysis failed",
                "details": str(e),
                "type": type(e).__name__
            }
    
    def _generate_action_items(self, warning_level, demand_change, tariff_percentage):
        """Generate specific action items based on impact analysis"""
        actions = []
        
        if warning_level == "HIGH":
            actions.extend([
                "🚨 URGENT: Review and potentially reduce incoming orders",
                f"📉 Expect approximately {abs(demand_change*100):.1f}% reduction in demand",
                "💰 Consider negotiating with suppliers for better terms",
                "🔄 Evaluate alternative sourcing options",
                "📊 Implement weekly demand monitoring"
            ])
        elif warning_level == "MEDIUM":
            actions.extend([
                "⚠️ Monitor stock levels more frequently",
                "📈 Adjust pricing strategy to maintain margins",
                "🏷️ Review promotional strategies",
                "📦 Optimize inventory levels"
            ])
        else:
            actions.extend([
                "✅ Maintain regular stock levels",
                "📊 Monitor market conditions",
                "📝 Document tariff impact for future reference"
            ])
            
        return actions
    
    def _analyze_category_impact(self, category_data, tariff_percentage):
        """Analyze category-level impact and generate recommendations"""
        recent_data = category_data[category_data['date'] >= datetime.now() - timedelta(days=30)]
        total_revenue = recent_data['price'].mean() * recent_data['sales'].sum()
        
        impact = {
            "estimated_revenue_impact": round(total_revenue * (tariff_percentage/100), 2),
            "affected_products_count": len(category_data['product_id'].unique()),
            "high_risk_products": len(category_data[category_data['sales'] > category_data['sales'].quantile(0.75)]['product_id'].unique()),
            "recommendations": [
                "Review supply chain alternatives",
                "Consider strategic price adjustments",
                "Evaluate inventory holding costs",
                "Monitor competitor responses",
                "Assess customer sensitivity"
            ]
        }
        
        return impact
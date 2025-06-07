import os
import json
import asyncio
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI-powered code analysis using Gemini"""
    
    def __init__(self, max_commits: Optional[int] = None):
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Cache for expensive operations
        self.analysis_cache = {}
        
        # Set max commits (None means no limit)
        self.max_commits = max_commits
    
    async def analyze_codebase(self, repo_data: Dict[str, Any], commit_analysis: Dict[str, Any], num_commits: Optional[int] = None) -> Dict[str, Any]:
        """Perform comprehensive AI analysis of the codebase"""
        
        try:
            logger.info("Starting AI codebase analysis")
            
            # Prepare analysis context with configurable commit count
            context = self._prepare_analysis_context(repo_data, commit_analysis, num_commits)
            
            # Run parallel analysis tasks
            tasks = [
                self._analyze_architecture(context),
                self._analyze_code_quality(context),
                self._identify_patterns(context),
                self._detect_technical_debt(context)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results
            analysis_results = {
                "architecture_analysis": results[0] if not isinstance(results[0], Exception) else {"error": str(results[0])},
                "code_quality": results[1] if not isinstance(results[1], Exception) else {"error": str(results[1])},
                "patterns": results[2] if not isinstance(results[2], Exception) else {"error": str(results[2])},
                "technical_debt": results[3] if not isinstance(results[3], Exception) else {"error": str(results[3])},
                "total_files": repo_data["file_structure"]["total_files"],
                "total_lines": repo_data["file_structure"]["total_lines"],
                "languages": repo_data["file_structure"]["languages"],
                "commits_analyzed": len(context["commit_history"]),
                "analysis_timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Completed AI codebase analysis for {len(context['commit_history'])} commits")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in AI codebase analysis: {e}")
            return {"error": str(e)}
    
    def _prepare_analysis_context(self, repo_data: Dict[str, Any], commit_analysis: Dict[str, Any], num_commits: Optional[int] = None) -> Dict[str, Any]:
        """Prepare context for AI analysis with configurable commit count"""
        
        # Determine how many commits to analyze
        commits = commit_analysis["commits"]
        
        if num_commits is not None:
            # Use the specified number of commits
            commits_to_analyze = commits[:num_commits]
        elif self.max_commits is not None:
            # Use the instance max_commits limit
            commits_to_analyze = commits[:self.max_commits]
        else:
            # No limit - use all commits
            commits_to_analyze = commits
        
        logger.info(f"Analyzing {len(commits_to_analyze)} out of {len(commits)} total commits")
        
        return {
            "repository_info": repo_data["info"],
            "file_structure": repo_data["file_structure"],
            "commit_history": commits_to_analyze,
            "commit_patterns": commit_analysis["analysis"],
            "repo_path": repo_data["path"]
        }
    
    async def _analyze_architecture(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the overall architecture of the codebase"""
        
        try:
            # Use first 5 commits for architecture analysis to avoid token limits
            recent_commits = context['commit_history'][:5]
            
            prompt = f"""
            As an expert software architect, analyze this codebase and provide insights:

            Repository Information:
            - Languages: {context['file_structure']['languages']}
            - Total Files: {context['file_structure']['total_files']}
            - File Types: {context['file_structure']['file_types']}
            - Directories: {context['file_structure']['directories'][:20]}

            Recent Commits ({len(recent_commits)} of {len(context['commit_history'])} total):
            {self._format_commits_for_prompt(recent_commits)}

            Please analyze and provide:
            1. Overall architecture pattern (MVC, Microservices, Monolith, etc.)
            2. Technology stack assessment
            3. Code organization quality
            4. Potential architectural improvements
            5. Scalability considerations

            Respond in JSON format with clear sections.
            """
            
            response = await self._call_gemini(prompt)
            return self._parse_ai_response(response, "architecture")
            
        except Exception as e:
            logger.error(f"Error in architecture analysis: {e}")
            return {"error": str(e)}
    
    async def _analyze_code_quality(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze code quality metrics and issues"""
        
        try:
            prompt = f"""
            As a senior code reviewer, analyze this codebase for quality metrics:

            File Structure:
            - Total Lines: {context['file_structure']['total_lines']}
            - Languages: {context['file_structure']['languages']}
            - Large Files: {context['file_structure']['large_files'][:5]}

            Commit Patterns (based on {len(context['commit_history'])} commits):
            - Average Commit Size: {context['commit_patterns'].get('average_commit_size', 0)}
            - Total Authors: {context['commit_patterns'].get('total_authors', 0)}
            - Top Authors: {context['commit_patterns'].get('top_authors', [])[:3]}

            Analyze and provide:
            1. Code quality score (1-10)
            2. Maintainability assessment
            3. Testing coverage estimation
            4. Documentation quality
            5. Code complexity indicators
            6. Specific improvement recommendations

            Respond in JSON format with metrics and explanations.
            """
            
            response = await self._call_gemini(prompt)
            return self._parse_ai_response(response, "code_quality")
            
        except Exception as e:
            logger.error(f"Error in code quality analysis: {e}")
            return {"error": str(e)}
    
    async def _identify_patterns(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Identify patterns and design patterns in the codebase"""
        
        try:
            # Use first 3 commits for pattern analysis
            recent_commits = context['commit_history'][:3]
            
            prompt = f"""
            As a software design pattern expert, analyze this codebase:

            Repository Structure:
            - Languages: {context['file_structure']['languages']}
            - Directories: {context['file_structure']['directories'][:15]}
            - File Types: {context['file_structure']['file_types']}

            Commit History ({len(recent_commits)} recent of {len(context['commit_history'])} total):
            {self._format_commits_for_prompt(recent_commits)}

            Identify and analyze:
            1. Design patterns used (Singleton, Factory, Observer, etc.)
            2. Architectural patterns
            3. Code organization patterns
            4. Naming conventions
            5. Common anti-patterns
            6. Recommended pattern improvements

            Respond in JSON format with detailed explanations.
            """
            
            response = await self._call_gemini(prompt)
            return self._parse_ai_response(response, "patterns")
            
        except Exception as e:
            logger.error(f"Error in pattern analysis: {e}")
            return {"error": str(e)}
    
    async def _detect_technical_debt(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Detect technical debt and areas for improvement"""
        
        try:
            prompt = f"""
            As a technical debt specialist, analyze this codebase:

            Repository Metrics:
            - Total Files: {context['file_structure']['total_files']}
            - Total Lines: {context['file_structure']['total_lines']}
            - Languages: {context['file_structure']['languages']}
            - Large Files: {context['file_structure']['large_files'][:5]}

            Commit Analysis (based on {len(context['commit_history'])} commits):
            - Recent commits analyzed: {len(context['commit_history'])}
            - Top authors: {context['commit_patterns'].get('top_authors', [])[:3]}

            Identify technical debt indicators:
            1. Code duplication likelihood
            2. Large file concerns
            3. Potential refactoring opportunities
            4. Maintenance complexity
            5. Performance bottlenecks
            6. Security considerations
            7. Prioritized improvement recommendations

            Respond in JSON format with severity levels and actionable insights.
            """
            
            response = await self._call_gemini(prompt)
            return self._parse_ai_response(response, "technical_debt")
            
        except Exception as e:
            logger.error(f"Error in technical debt analysis: {e}")
            return {"error": str(e)}
    
    async def generate_insights(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate high-level insights from analysis results"""
        
        try:
            commits_analyzed = analysis_results.get('commits_analyzed', 'unknown')
            
            prompt = f"""
            As a senior software consultant, provide executive insights based on this analysis:

            Analysis Results (based on {commits_analyzed} commits):
            {json.dumps(analysis_results, indent=2)[:3000]}...

            Generate:
            1. Executive summary (2-3 sentences)
            2. Key strengths of the codebase
            3. Critical areas for improvement
            4. Risk assessment
            5. Recommended next steps
            6. Overall health score (1-10)

            Respond in JSON format with clear, actionable insights.
            """
            
            response = await self._call_gemini(prompt)
            return self._parse_ai_response(response, "insights")
            
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return {"error": str(e)}
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API with error handling"""
        
        try:
            # Add rate limiting logic here if needed
            response = await asyncio.to_thread(
                self.model.generate_content,
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,
                    max_output_tokens=2048,
                )
            )
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            raise
    
    def _parse_ai_response(self, response: str, analysis_type: str) -> Dict[str, Any]:
        """Parse AI response and extract structured data"""
        
        try:
            # Try to parse as JSON first
            if response.strip().startswith('{'):
                return json.loads(response)
            
            # If not JSON, create structured response
            return {
                "type": analysis_type,
                "analysis": response,
                "timestamp": datetime.now().isoformat(),
                "parsed": False
            }
            
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            return {
                "type": analysis_type,
                "analysis": response,
                "timestamp": datetime.now().isoformat(),
                "parsed": False
            }
    
    def _format_commits_for_prompt(self, commits: List[Dict[str, Any]]) -> str:
        """Format commits for AI prompt"""
        
        if not commits:
            return "No recent commits available"
        
        formatted = []
        for commit in commits[:5]:  # Limit to 5 to avoid token limits in prompts
            formatted.append(f"- {commit.get('message', 'No message')[:100]}...")
        
        return "\n".join(formatted)
    
    async def create_visualizations(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Create data for visualizations"""
        
        try:
            # Extract metrics for visualization
            visualizations = {
                "quality_metrics": {
                    "code_quality": insights.get("code_quality", {}).get("score", 5),
                    "maintainability": insights.get("code_quality", {}).get("maintainability", 5),
                    "technical_debt": insights.get("technical_debt", {}).get("severity", 5)
                },
                "architecture_overview": {
                    "pattern": insights.get("architecture_analysis", {}).get("pattern", "Unknown"),
                    "complexity": insights.get("architecture_analysis", {}).get("complexity", "Medium")
                },
                "improvement_priorities": self._extract_priorities(insights),
                "trend_data": self._generate_trend_data(insights)
            }
            
            return visualizations
            
        except Exception as e:
            logger.error(f"Error creating visualizations: {e}")
            return {"error": str(e)}
    
    def _extract_priorities(self, insights: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract improvement priorities from insights"""
        
        priorities = []
        
        # Extract from technical debt
        if "technical_debt" in insights:
            debt_data = insights["technical_debt"]
            if isinstance(debt_data, dict) and "recommendations" in debt_data:
                for rec in debt_data["recommendations"][:5]:
                    priorities.append({
                        "category": "Technical Debt",
                        "priority": "High",
                        "description": rec
                    })
        
        # Extract from code quality
        if "code_quality" in insights:
            quality_data = insights["code_quality"]
            if isinstance(quality_data, dict) and "improvements" in quality_data:
                for imp in quality_data["improvements"][:3]:
                    priorities.append({
                        "category": "Code Quality",
                        "priority": "Medium",
                        "description": imp
                    })
        
        return priorities[:10]  # Limit to top 10
    
    def _generate_trend_data(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Generate trend data for charts"""
        
        return {
            "timeline": ["Week 1", "Week 2", "Week 3", "Week 4"],
            "quality_trend": [6, 7, 7, 8],  # Placeholder data
            "debt_trend": [8, 7, 6, 5],     # Placeholder data
            "complexity_trend": [5, 5, 6, 6] # Placeholder data
        }
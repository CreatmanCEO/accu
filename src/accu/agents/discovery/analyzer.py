"""Repository analyzer for Discovery Agent."""

import json

from accu.agents.discovery.models import (
    AIAnalysis,
    DiscoveryConfig,
    RepositorySignals,
)
from accu.providers import CompletionRequest, Message, ProviderManager


ANALYSIS_SYSTEM_PROMPT = """You are a technical analyst evaluating open-source repositories for revival potential.

Your task is to analyze a repository and provide:
1. A brief summary of what the project does
2. Key strengths of the codebase
3. Key weaknesses or areas needing improvement
4. Recommendation for revival effort (low/medium/high)
5. Estimated hours to bring to production quality
6. Target audience for this project

Be concise and factual. Focus on technical aspects, not popularity.

Respond in JSON format:
{
    "summary": "...",
    "strengths": ["...", "..."],
    "weaknesses": ["...", "..."],
    "revival_recommendation": "low|medium|high effort, [reason]",
    "estimated_effort_hours": 100,
    "target_audience": "..."
}"""


class RepositoryAnalyzer:
    """Analyzes repositories using AI and heuristics."""

    def __init__(
        self,
        provider_manager: ProviderManager,
        config: DiscoveryConfig,
    ):
        self.ai = provider_manager
        self.config = config

    async def analyze(
        self,
        repo: dict,
        readme_content: str | None = None,
    ) -> tuple[RepositorySignals, AIAnalysis | None]:
        """Analyze a repository and return signals and AI analysis.

        Args:
            repo: Repository data from GitHub API
            readme_content: Optional README content

        Returns:
            Tuple of (RepositorySignals, AIAnalysis or None)
        """
        # Calculate basic signals from metadata
        signals = self._calculate_signals(repo)

        # Perform AI analysis if enabled
        ai_analysis = None
        if self.config.analyze_readme and readme_content:
            ai_analysis = await self._ai_analyze(repo, readme_content)

            # Update signals based on AI analysis
            if ai_analysis:
                signals = self._update_signals_from_ai(signals, ai_analysis)

        return signals, ai_analysis

    def _calculate_signals(self, repo: dict) -> RepositorySignals:
        """Calculate signals from repository metadata."""
        # Check for common files
        has_readme = repo.get("has_readme", False) or repo.get("description") is not None
        has_license = repo.get("license") is not None

        # Estimate abandonment
        from datetime import datetime, timedelta
        pushed_at = repo.get("pushed_at")
        is_abandoned = False
        if pushed_at:
            try:
                pushed_date = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
                is_abandoned = (datetime.now(pushed_date.tzinfo) - pushed_date) > timedelta(days=365)
            except Exception:
                pass

        return RepositorySignals(
            is_abandoned=is_abandoned,
            has_readme=has_readme,
            has_license=has_license,
            has_tests=False,  # Will be updated by file analysis
            has_ci=False,
            has_documentation=has_readme,
            documentation_quality=0.5 if has_readme else 0.0,
            code_quality_estimate=0.5,  # Default, updated by AI
        )

    async def _ai_analyze(
        self,
        repo: dict,
        readme_content: str,
    ) -> AIAnalysis | None:
        """Perform AI analysis on repository."""
        try:
            # Build prompt
            prompt = self._build_analysis_prompt(repo, readme_content)

            # Get AI analysis
            request = CompletionRequest(
                messages=[
                    Message(role="system", content=ANALYSIS_SYSTEM_PROMPT),
                    Message(role="user", content=prompt),
                ],
                max_tokens=1000,
                temperature=0.3,  # Lower temperature for more consistent analysis
            )

            response = await self.ai.complete(request)

            # Parse JSON response
            return self._parse_ai_response(response.content)

        except Exception as e:
            # Log error but don't fail the analysis
            print(f"AI analysis failed for {repo.get('full_name')}: {e}")
            return None

    def _build_analysis_prompt(self, repo: dict, readme_content: str) -> str:
        """Build the analysis prompt."""
        # Truncate README if too long
        max_readme_length = 4000
        if len(readme_content) > max_readme_length:
            readme_content = readme_content[:max_readme_length] + "\n\n[README truncated...]"

        return f"""Analyze this repository:

**Repository:** {repo.get('full_name')}
**Description:** {repo.get('description', 'No description')}
**Language:** {repo.get('language', 'Unknown')}
**Stars:** {repo.get('stargazers_count', 0)}
**Forks:** {repo.get('forks_count', 0)}
**Open Issues:** {repo.get('open_issues_count', 0)}
**Topics:** {', '.join(repo.get('topics', []))}
**License:** {repo.get('license', {}).get('name', 'Unknown') if repo.get('license') else 'None'}
**Created:** {repo.get('created_at', 'Unknown')}
**Last Push:** {repo.get('pushed_at', 'Unknown')}

**README Content:**
```
{readme_content}
```

Analyze this repository for revival potential."""

    def _parse_ai_response(self, content: str) -> AIAnalysis | None:
        """Parse AI response JSON."""
        try:
            # Try to extract JSON from response
            content = content.strip()

            # Handle markdown code blocks
            if content.startswith("```"):
                lines = content.split("\n")
                content = "\n".join(lines[1:-1])

            data = json.loads(content)

            return AIAnalysis(
                summary=data.get("summary", ""),
                strengths=data.get("strengths", []),
                weaknesses=data.get("weaknesses", []),
                revival_recommendation=data.get("revival_recommendation", ""),
                estimated_effort_hours=data.get("estimated_effort_hours"),
                target_audience=data.get("target_audience", ""),
            )
        except (json.JSONDecodeError, KeyError):
            return None

    def _update_signals_from_ai(
        self,
        signals: RepositorySignals,
        ai_analysis: AIAnalysis,
    ) -> RepositorySignals:
        """Update signals based on AI analysis."""
        # Estimate code quality from AI recommendation
        recommendation = ai_analysis.revival_recommendation.lower()
        if "low" in recommendation:
            signals.code_quality_estimate = 0.8
        elif "medium" in recommendation:
            signals.code_quality_estimate = 0.6
        elif "high" in recommendation:
            signals.code_quality_estimate = 0.4

        # Check for test mentions in strengths
        for strength in ai_analysis.strengths:
            if "test" in strength.lower():
                signals.has_tests = True
                break

        # Adjust documentation quality based on strengths/weaknesses
        doc_mentions = sum(
            1 for s in ai_analysis.strengths if "doc" in s.lower()
        ) - sum(
            1 for w in ai_analysis.weaknesses if "doc" in w.lower()
        )
        signals.documentation_quality = min(1.0, max(0.0, 0.5 + doc_mentions * 0.2))

        return signals

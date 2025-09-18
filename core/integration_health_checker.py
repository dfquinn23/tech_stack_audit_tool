# core/integration_health_checker.py
"""
Systematic integration health assessment and gap analysis
Eliminates guesswork in understanding how tools connect and where improvements are needed
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class IntegrationStatus(Enum):
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    BROKEN = "broken"
    MISSING = "missing"
    UNKNOWN = "unknown"


class IntegrationType(Enum):
    API = "api"
    WEBHOOK = "webhook"
    DATABASE = "database"
    FILE_SYNC = "file_sync"
    EMAIL_SYNC = "email_sync"
    CALENDAR_SYNC = "calendar_sync"
    SSO = "sso"
    MANUAL = "manual"
    NONE = "none"
    UNKNOWN = "unknown"


@dataclass
class IntegrationAssessment:
    source_tool: str
    target_tool: str
    integration_type: IntegrationType
    status: IntegrationStatus
    health_score: int  # 0-100
    last_sync: Optional[datetime]
    error_rate: float  # 0.0-1.0
    data_flow_direction: str  # "bidirectional", "source_to_target", "target_to_source"
    business_criticality: str  # "high", "medium", "low"
    issues_found: List[str]
    recommendations: List[str]
    assessment_timestamp: datetime


def safe_enum_to_string(enum_obj):
    """Safely convert enum to string, handling both enum objects and strings"""
    if hasattr(enum_obj, 'value'):
        return enum_obj.value
    else:
        return str(enum_obj)


class IntegrationHealthChecker:
    """Systematic integration health assessment and gap analysis"""

    def __init__(self):
        # Cache health checks for 6 hours
        self.cache_duration = timedelta(hours=6)
        self.cache_dir = Path("data/integration_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Known integration patterns for common business tools
        self.integration_patterns = {
            # Microsoft 365 integrations
            ("365", "zoom"): {
                "expected_type": IntegrationType.CALENDAR_SYNC,
                "data_flow": "bidirectional",
                "criticality": "high",
                "common_issues": ["calendar sync failures", "authentication expiry", "timezone conflicts"]
            },
            ("365", "slack"): {
                "expected_type": IntegrationType.EMAIL_SYNC,
                "data_flow": "source_to_target",
                "criticality": "medium",
                "common_issues": ["notification overload", "attachment size limits"]
            },

            # CRM integrations
            ("wealth box", "365"): {
                "expected_type": IntegrationType.EMAIL_SYNC,
                "data_flow": "bidirectional",
                "criticality": "high",
                "common_issues": ["contact sync delays", "duplicate entries", "field mapping errors"]
            },
            ("wealth box", "zoom"): {
                "expected_type": IntegrationType.CALENDAR_SYNC,
                "data_flow": "bidirectional",
                "criticality": "medium",
                "common_issues": ["meeting link generation", "attendee sync issues"]
            },

            # Financial data integrations
            ("factset", "365"): {
                "expected_type": IntegrationType.FILE_SYNC,
                "data_flow": "source_to_target",
                "criticality": "high",
                "common_issues": ["data export formatting", "access permissions", "report delivery timing"]
            },
            ("bloomberg", "365"): {
                "expected_type": IntegrationType.FILE_SYNC,
                "data_flow": "source_to_target",
                "criticality": "high",
                "common_issues": ["terminal export limits", "file format compatibility", "real-time data delays"]
            },
            ("advent axys", "wealth box"): {
                "expected_type": IntegrationType.DATABASE,
                "data_flow": "source_to_target",
                "criticality": "high",
                "common_issues": ["portfolio data sync", "client mapping", "performance attribution delays"]
            },

            # Custodial integrations
            ("schwab", "advent axys"): {
                "expected_type": IntegrationType.FILE_SYNC,
                "data_flow": "source_to_target",
                "criticality": "high",
                "common_issues": ["trade settlement timing", "position reconciliation", "corporate action processing"]
            },
            ("schwab", "wealth box"): {
                "expected_type": IntegrationType.DATABASE,
                "data_flow": "source_to_target",
                "criticality": "medium",
                "common_issues": ["account opening sync", "document management", "client onboarding delays"]
            }
        }

        # API endpoints for health checking (where available)
        self.health_endpoints = {
            "zoom": "https://api.zoom.us/v2/users/me",
            "365": "https://graph.microsoft.com/v1.0/me",
            "slack": "https://slack.com/api/auth.test",
            "github": "https://api.github.com/user"
        }

    def _normalize_tool_name(self, tool_name: str) -> str:
        """Normalize tool names for consistent lookup"""
        normalized = tool_name.lower().strip()
        # Handle common variations
        if "microsoft" in normalized or "office" in normalized:
            return "365"
        if "wealthbox" in normalized or "wealth box" in normalized:
            return "wealth box"
        if "advent" in normalized:
            return "advent axys"
        return normalized

    def _get_integration_key(self, tool1: str, tool2: str) -> Tuple[str, str]:
        """Get normalized key for integration lookup (alphabetically ordered)"""
        norm1 = self._normalize_tool_name(tool1)
        norm2 = self._normalize_tool_name(tool2)
        return tuple(sorted([norm1, norm2]))

    def _sanitize_filename(self, filename: str) -> str:
        """Sanitize filename for cross-platform compatibility"""
        # Replace invalid characters with safe alternatives
        filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
        # Replace https:// and http://
        filename = re.sub(r'https?://', '', filename)
        # Replace multiple underscores with single
        filename = re.sub(r'_+', '_', filename)
        # Remove leading/trailing underscores and dots
        filename = filename.strip('_.')
        # Limit length to avoid filesystem limits
        if len(filename) > 100:
            filename = filename[:100]
        return filename

    async def assess_integration_health(self, source_tool: str, target_tool: str,
                                        current_integration_data: Optional[Dict] = None) -> IntegrationAssessment:
        """Assess the health of a specific integration"""

        # Check cache first
        cache_key = f"health_{self._normalize_tool_name(source_tool)}_{self._normalize_tool_name(target_tool)}"
        cached_result = self._load_cache(cache_key)
        if cached_result:
            return IntegrationAssessment(**cached_result)

        print(f"🔍 Assessing integration: {source_tool} → {target_tool}")

        # Get expected integration pattern
        integration_key = self._get_integration_key(source_tool, target_tool)
        expected_pattern = self.integration_patterns.get(integration_key)

        # Initialize assessment
        assessment = IntegrationAssessment(
            source_tool=source_tool,
            target_tool=target_tool,
            integration_type=IntegrationType.UNKNOWN,
            status=IntegrationStatus.UNKNOWN,
            health_score=0,
            last_sync=None,
            error_rate=0.0,
            data_flow_direction="unknown",
            business_criticality="unknown",
            issues_found=[],
            recommendations=[],
            assessment_timestamp=datetime.now()
        )

        # Use expected pattern if available
        if expected_pattern:
            assessment.integration_type = expected_pattern["expected_type"]
            assessment.data_flow_direction = expected_pattern["data_flow"]
            assessment.business_criticality = expected_pattern["criticality"]

        # Analyze current integration data if provided
        if current_integration_data:
            await self._analyze_existing_integration(assessment, current_integration_data)
        else:
            # No integration data provided - this might be a missing integration
            if expected_pattern:
                assessment.status = IntegrationStatus.MISSING
                assessment.issues_found.append(
                    "Expected integration not found")
                assessment.recommendations.append(
                    f"Implement {safe_enum_to_string(expected_pattern['expected_type'])} integration")
            else:
                assessment.status = IntegrationStatus.UNKNOWN
                assessment.issues_found.append(
                    "No integration pattern defined")

        # Perform API health checks where possible (TEMPORARILY DISABLED FOR DEBUGGING)
        # await self._perform_api_health_checks(assessment)
        print(f"   🔧 Skipping API health checks for debugging")

        # Calculate overall health score
        assessment.health_score = self._calculate_health_score(assessment)

        # Generate recommendations
        assessment.recommendations.extend(
            self._generate_recommendations(assessment, expected_pattern))

        # Cache the result (TEMPORARILY DISABLED FOR DEBUGGING)
        # self._save_cache(cache_key, assessment.__dict__)
        print(f"   🔧 Skipping cache save for debugging")

        print(
            f"   Status: {safe_enum_to_string(assessment.status)}, Health Score: {assessment.health_score}/100")

        return assessment

    async def _analyze_existing_integration(self, assessment: IntegrationAssessment, integration_data: Dict):
        """Analyze existing integration data to determine health"""

        # Extract information from integration data
        if "status" in integration_data:
            try:
                assessment.status = IntegrationStatus(
                    integration_data["status"].lower())
            except ValueError:
                assessment.status = IntegrationStatus.UNKNOWN

        if "integration_type" in integration_data:
            try:
                assessment.integration_type = IntegrationType(
                    integration_data["integration_type"].lower())
            except ValueError:
                assessment.integration_type = IntegrationType.UNKNOWN

        if "health_score" in integration_data:
            assessment.health_score = max(
                0, min(100, int(integration_data.get("health_score", 0))))

        if "error_rate" in integration_data:
            assessment.error_rate = max(
                0.0, min(1.0, float(integration_data.get("error_rate", 0.0))))

        if "last_sync" in integration_data:
            try:
                assessment.last_sync = datetime.fromisoformat(
                    integration_data["last_sync"])
            except (ValueError, TypeError):
                pass

        # Analyze sync recency
        if assessment.last_sync:
            days_since_sync = (datetime.now() - assessment.last_sync).days
            if days_since_sync > 7:
                assessment.issues_found.append(
                    f"Last sync was {days_since_sync} days ago")
            elif days_since_sync > 1:
                assessment.issues_found.append(
                    f"Sync may be delayed ({days_since_sync} days)")

        # Analyze error rates
        if assessment.error_rate > 0.1:  # 10%+ error rate
            assessment.issues_found.append(
                f"High error rate: {assessment.error_rate:.1%}")
        elif assessment.error_rate > 0.05:  # 5%+ error rate
            assessment.issues_found.append(
                f"Elevated error rate: {assessment.error_rate:.1%}")

    async def _perform_api_health_checks(self, assessment: IntegrationAssessment):
        """Perform API health checks where endpoints are available"""

        source_normalized = self._normalize_tool_name(assessment.source_tool)
        target_normalized = self._normalize_tool_name(assessment.target_tool)

        # Check if we can test API connectivity
        source_endpoint = self.health_endpoints.get(source_normalized)
        target_endpoint = self.health_endpoints.get(target_normalized)

        if source_endpoint or target_endpoint:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:

                    # Test source API
                    if source_endpoint:
                        source_healthy = await self._test_api_endpoint(session, source_endpoint)
                        if not source_healthy:
                            assessment.issues_found.append(
                                f"Source API ({assessment.source_tool}) unreachable")

                    # Test target API
                    if target_endpoint:
                        target_healthy = await self._test_api_endpoint(session, target_endpoint)
                        if not target_healthy:
                            assessment.issues_found.append(
                                f"Target API ({assessment.target_tool}) unreachable")

            except Exception as e:
                assessment.issues_found.append(
                    f"API health check failed: {str(e)}")

    async def _test_api_endpoint(self, session: aiohttp.ClientSession, endpoint: str) -> bool:
        """Test if an API endpoint is reachable and responding"""
        try:
            async with session.get(endpoint) as response:
                # 200 = OK, 401 = Unauthorized (but API is responding), 403 = Forbidden (but API is responding)
                return response.status in [200, 401, 403]
        except Exception:
            return False

    def _calculate_health_score(self, assessment: IntegrationAssessment) -> int:
        """Calculate overall health score (0-100) based on various factors"""

        base_score = 50  # Start with neutral score

        # Status-based scoring
        status_scores = {
            IntegrationStatus.HEALTHY: 90,
            IntegrationStatus.DEGRADED: 60,
            IntegrationStatus.BROKEN: 20,
            IntegrationStatus.MISSING: 0,
            IntegrationStatus.UNKNOWN: 30
        }

        base_score = status_scores.get(assessment.status, 30)

        # Adjust for error rate
        if assessment.error_rate > 0:
            # High error rate reduces score significantly
            base_score -= (assessment.error_rate * 50)

        # Adjust for sync recency
        if assessment.last_sync:
            days_since_sync = (datetime.now() - assessment.last_sync).days
            if days_since_sync <= 1:
                base_score += 10  # Recent sync is good
            elif days_since_sync > 7:
                base_score -= 20  # Old sync is bad

        # Adjust for business criticality
        if assessment.business_criticality == "high":
            # High criticality integrations get penalized more for issues
            if len(assessment.issues_found) > 0:
                base_score -= (len(assessment.issues_found) * 10)

        # Ensure score stays in valid range
        return max(0, min(100, int(base_score)))

    def _generate_recommendations(self, assessment: IntegrationAssessment, expected_pattern: Optional[Dict]) -> List[str]:
        """Generate specific recommendations for integration improvement"""
        recommendations = []

        if assessment.status == IntegrationStatus.MISSING and expected_pattern:
            recommendations.append(
                f"Implement {safe_enum_to_string(expected_pattern['expected_type'])} integration between {assessment.source_tool} and {assessment.target_tool}")
            recommendations.append(
                f"Expected business value: Improved {expected_pattern['data_flow']} data flow")

            # Add common issue prevention
            common_issues = expected_pattern.get("common_issues", [])
            if common_issues:
                recommendations.append(
                    f"Prevent common issues: {', '.join(common_issues)}")

        elif assessment.status == IntegrationStatus.BROKEN:
            recommendations.append(
                f"Investigate and repair broken integration")
            recommendations.append(
                f"Review error logs and authentication status")
            if assessment.error_rate > 0.2:
                recommendations.append(
                    f"Address high error rate ({assessment.error_rate:.1%})")

        elif assessment.status == IntegrationStatus.DEGRADED:
            recommendations.append(f"Optimize integration performance")
            if assessment.error_rate > 0.05:
                recommendations.append(
                    f"Reduce error rate from {assessment.error_rate:.1%}")
            if assessment.last_sync and (datetime.now() - assessment.last_sync).days > 3:
                recommendations.append(
                    f"Improve sync frequency (last sync: {assessment.last_sync.strftime('%Y-%m-%d')})")

        elif assessment.status == IntegrationStatus.HEALTHY:
            recommendations.append(f"Monitor integration health regularly")
            if assessment.health_score < 80:
                recommendations.append(
                    f"Consider optimization opportunities to improve health score")

        # Add business impact recommendations
        if assessment.business_criticality == "high" and assessment.health_score < 70:
            recommendations.append(
                f"HIGH PRIORITY: Critical business integration needs immediate attention")

        return recommendations

    async def assess_complete_integration_matrix(self, tool_inventory: Dict[str, dict]) -> Dict[str, IntegrationAssessment]:
        """Assess all possible integrations between tools in the inventory"""

        tools = list(tool_inventory.keys())
        assessments = {}

        print(f"🔍 Assessing integration matrix for {len(tools)} tools...")
        print(f"   Expected assessments: {len(tools) * (len(tools) - 1) // 2}")

        # Create tasks for all tool pairs
        tasks = []
        tool_pairs = []

        for i, source_tool in enumerate(tools):
            for j, target_tool in enumerate(tools):
                if i < j:  # Avoid duplicate pairs and self-integration
                    tasks.append(self.assess_integration_health(
                        source_tool, target_tool))
                    tool_pairs.append((source_tool, target_tool))

        # Execute assessments concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for (source_tool, target_tool), result in zip(tool_pairs, results):
            if isinstance(result, IntegrationAssessment):
                key = f"{source_tool}→{target_tool}"
                assessments[key] = result
            elif isinstance(result, Exception):
                print(
                    f"⚠️ Assessment failed for {source_tool}→{target_tool}: {result}")

        print(
            f"✅ Integration matrix completed: {len(assessments)} assessments")

        return assessments

    def generate_integration_summary(self, assessments: Dict[str, IntegrationAssessment]) -> Dict[str, Any]:
        """Generate summary statistics from integration assessments"""

        total = len(assessments)
        if total == 0:
            return {
                "error": "No assessments to summarize",
                "summary_timestamp": datetime.now().isoformat(),
                "total_integrations_assessed": 0,
                "average_health_score": 0,
                "status_distribution": {},
                "criticality_distribution": {},
                "top_issues": [],
                "critical_integrations_needing_attention": [],
                "healthy_integrations": 0,
                "missing_integrations": 0,
                "broken_integrations": 0
            }

        # Status distribution
        status_counts = {}
        for assessment in assessments.values():
            status = safe_enum_to_string(assessment.status)
            status_counts[status] = status_counts.get(status, 0) + 1

        # Health score distribution
        health_scores = [a.health_score for a in assessments.values()]
        avg_health = sum(health_scores) / len(health_scores)

        # Business criticality distribution
        criticality_counts = {}
        for assessment in assessments.values():
            crit = assessment.business_criticality
            criticality_counts[crit] = criticality_counts.get(crit, 0) + 1

        # Top issues
        all_issues = []
        for assessment in assessments.values():
            all_issues.extend(assessment.issues_found)

        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1

        top_issues = sorted(issue_counts.items(),
                            key=lambda x: x[1], reverse=True)[:10]

        # Critical integrations needing attention
        critical_issues = [
            {"integration": key, "health_score": assessment.health_score,
                "status": safe_enum_to_string(assessment.status)}
            for key, assessment in assessments.items()
            if assessment.business_criticality == "high" and assessment.health_score < 70
        ]
        critical_issues.sort(key=lambda x: x["health_score"])

        return {
            "summary_timestamp": datetime.now().isoformat(),
            "total_integrations_assessed": total,
            "average_health_score": round(avg_health, 1),
            "status_distribution": status_counts,
            "criticality_distribution": criticality_counts,
            "top_issues": top_issues,
            "critical_integrations_needing_attention": critical_issues[:5],
            "healthy_integrations": len([a for a in assessments.values() if a.status == IntegrationStatus.HEALTHY]),
            "missing_integrations": len([a for a in assessments.values() if a.status == IntegrationStatus.MISSING]),
            "broken_integrations": len([a for a in assessments.values() if a.status == IntegrationStatus.BROKEN])
        }

    def _load_cache(self, cache_key: str) -> Optional[Dict]:
        """Load cached assessment if still valid"""
        sanitized_key = self._sanitize_filename(cache_key)
        cache_file = self.cache_dir / f"{sanitized_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    cached_time = datetime.fromisoformat(
                        data.get('cached_at', ''))
                    if datetime.now() - cached_time < self.cache_duration:
                        return data.get('assessment')
            except Exception:
                pass
        return None

    def _save_cache(self, cache_key: str, assessment_dict: Dict):
        """Save assessment to cache"""
        # Convert datetime objects to strings for JSON serialization
        serializable_dict = {}
        for key, value in assessment_dict.items():
            if hasattr(value, 'isoformat'):  # datetime object
                serializable_dict[key] = value.isoformat()
            elif isinstance(value, list):
                # Handle lists that might contain non-serializable objects
                serializable_dict[key] = [str(item) if hasattr(
                    item, '__dict__') else item for item in value]
            elif hasattr(value, 'value'):  # enum object
                serializable_dict[key] = value.value
            else:
                serializable_dict[key] = value

        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'assessment': serializable_dict
        }
        sanitized_key = self._sanitize_filename(cache_key)
        cache_file = self.cache_dir / f"{sanitized_key}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
        except Exception as e:
            print(f"   ⚠️ Cache save failed for {cache_key}: {e}")

# Convenience functions for quick usage


async def quick_integration_assessment(tool1: str, tool2: str) -> IntegrationAssessment:
    """Quick assessment of a single integration"""
    checker = IntegrationHealthChecker()
    return await checker.assess_integration_health(tool1, tool2)


async def assess_tool_stack_integrations(tool_inventory: Dict[str, dict]) -> Tuple[Dict[str, IntegrationAssessment], Dict[str, Any]]:
    """Assess all integrations in a tool stack and return summary"""
    checker = IntegrationHealthChecker()
    assessments = await checker.assess_complete_integration_matrix(tool_inventory)
    summary = checker.generate_integration_summary(assessments)
    return assessments, summary

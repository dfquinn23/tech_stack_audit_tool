# core/discovery_engine.py
import asyncio
import aiohttp
import dns.resolver
import socket
import ssl
import requests
from typing import Dict, List, Optional, Tuple, Any
from urllib.parse import urlparse
import json
from datetime import datetime, timedelta
import re
from pathlib import Path

class DiscoveryEngine:
    def __init__(self, cache_duration_hours: int = 24):
        self.cache_duration = timedelta(hours=cache_duration_hours)
        self.cache_dir = Path("data/discovery_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Known SaaS patterns for detection
        self.saas_patterns = {
            'zoom': {
                'domains': ['zoom.us', 'zoomgov.com'],
                'subdomains': ['*.zoom.us'],
                'api_endpoint': 'https://api.zoom.us/v2/',
                'category': 'Video Conferencing'
            },
            'microsoft365': {
                'domains': ['outlook.office.com', 'teams.microsoft.com', 'office.com'],
                'subdomains': ['*.sharepoint.com', '*.onmicrosoft.com'],
                'api_endpoint': 'https://graph.microsoft.com/v1.0/',
                'category': 'Productivity Suite'
            },
            'slack': {
                'domains': ['slack.com'],
                'subdomains': ['*.slack.com'],
                'api_endpoint': 'https://slack.com/api/',
                'category': 'Communication'
            },
            'salesforce': {
                'domains': ['salesforce.com', 'force.com'],
                'subdomains': ['*.salesforce.com', '*.force.com'],
                'api_endpoint': 'https://api.salesforce.com/',
                'category': 'CRM'
            },
            'google_workspace': {
                'domains': ['gmail.com', 'googlemail.com'],
                'subdomains': ['*.google.com'],
                'api_endpoint': 'https://www.googleapis.com/',
                'category': 'Productivity Suite'
            },
            'atlassian': {
                'domains': ['atlassian.net', 'atlassian.com'],
                'subdomains': ['*.atlassian.net'],
                'api_endpoint': 'https://api.atlassian.com/',
                'category': 'Development Tools'
            },
            'github': {
                'domains': ['github.com', 'github.io'],
                'subdomains': ['*.github.com', '*.github.io'],
                'api_endpoint': 'https://api.github.com/',
                'category': 'Development Tools'
            },
            'aws': {
                'domains': ['amazonaws.com', 'aws.amazon.com'],
                'subdomains': ['*.amazonaws.com'],
                'api_endpoint': 'https://aws.amazon.com/',
                'category': 'Cloud Infrastructure'
            },
            'azure': {
                'domains': ['azure.com', 'azurewebsites.net'],
                'subdomains': ['*.azure.com', '*.azurewebsites.net'],
                'api_endpoint': 'https://management.azure.com/',
                'category': 'Cloud Infrastructure'
            }
        }
        
        # Common subdomain patterns to check
        self.common_subdomains = [
            'mail', 'email', 'mx', 'smtp', 'pop', 'imap',  # Email
            'zoom', 'meet', 'video', 'webex', 'gotomeeting',  # Video
            'slack', 'teams', 'chat', 'mattermost',  # Chat
            'jira', 'confluence', 'wiki', 'docs',  # Documentation
            'github', 'gitlab', 'git', 'svn',  # Version control
            'crm', 'sales', 'support', 'helpdesk',  # Business
            'api', 'app', 'portal', 'dashboard',  # Applications
            'cdn', 'assets', 'static', 'media',  # Content delivery
            'vpn', 'remote', 'rdp', 'ssh'  # Remote access
        ]
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Get cache file path for a given key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_cache_valid(self, cache_file: Path) -> bool:
        """Check if cache file is still valid"""
        if not cache_file.exists():
            return False
        
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(data.get('cached_at', ''))
                return datetime.now() - cached_time < self.cache_duration
        except Exception:
            return False
    
    def _save_cache(self, cache_key: str, data: Any):
        """Save data to cache"""
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'data': data
        }
        cache_file = self._get_cache_file(cache_key)
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
    
    def _load_cache(self, cache_key: str) -> Optional[Any]:
        """Load data from cache if valid"""
        cache_file = self._get_cache_file(cache_key)
        if self._is_cache_valid(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    return data['data']
            except Exception:
                pass
        return None
    
    async def discover_domain_footprint(self, domain: str) -> Dict[str, Any]:
        """Discover SaaS tools by analyzing domain DNS records and patterns"""
        cache_key = f"domain_footprint_{domain}"
        cached_result = self._load_cache(cache_key)
        if cached_result:
            print(f"📋 Using cached domain footprint for {domain}")
            return cached_result
        
        print(f"🔍 Discovering SaaS footprint for domain: {domain}")
        discovered_tools = {}
        
        # Check MX records (email providers)
        email_provider = await self._check_email_provider(domain)
        if email_provider:
            discovered_tools['email'] = email_provider
        
        # Check subdomain patterns
        subdomain_discoveries = await self._check_subdomains(domain)
        discovered_tools.update(subdomain_discoveries)
        
        # Check SSL certificates for additional domains
        ssl_discoveries = await self._check_ssl_certificates(domain)
        discovered_tools.update(ssl_discoveries)
        
        # Save to cache
        self._save_cache(cache_key, discovered_tools)
        
        print(f"✅ Discovered {len(discovered_tools)} services for {domain}")
        return discovered_tools
    
    async def _check_email_provider(self, domain: str) -> Optional[Dict]:
        """Check MX records to identify email provider"""
        try:
            resolver = dns.resolver.Resolver()
            resolver.timeout = 10
            mx_records = resolver.resolve(domain, 'MX')
            
            for mx in mx_records:
                mx_domain = str(mx.exchange).lower()
                
                # Check against known email providers
                if 'google' in mx_domain or 'gmail' in mx_domain:
                    return {
                        'tool': 'google_workspace',
                        'provider': 'Google Workspace',
                        'mx_record': mx_domain,
                        'category': 'Email/Productivity',
                        'discovery_method': 'mx_record'
                    }
                elif 'outlook' in mx_domain or 'office365' in mx_domain:
                    return {
                        'tool': 'microsoft365',
                        'provider': 'Microsoft 365',
                        'mx_record': mx_domain,
                        'category': 'Email/Productivity',
                        'discovery_method': 'mx_record'
                    }
                elif 'zoho' in mx_domain:
                    return {
                        'tool': 'zoho',
                        'provider': 'Zoho Mail',
                        'mx_record': mx_domain,
                        'category': 'Email/Productivity',
                        'discovery_method': 'mx_record'
                    }
        except Exception as e:
            print(f"⚠️ Error checking MX records for {domain}: {e}")
        
        return None
    
    async def _check_subdomains(self, domain: str) -> Dict[str, Any]:
        """Check common subdomains for SaaS patterns"""
        discoveries = {}
        
        # Use asyncio to check subdomains concurrently
        tasks = []
        for subdomain_prefix in self.common_subdomains:
            subdomain = f"{subdomain_prefix}.{domain}"
            tasks.append(self._check_single_subdomain(subdomain))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for i, result in enumerate(results):
            if isinstance(result, dict) and result:
                subdomain_prefix = self.common_subdomains[i]
                discoveries[f"subdomain_{subdomain_prefix}"] = result
        
        return discoveries
    
    async def _check_single_subdomain(self, subdomain: str) -> Optional[Dict]:
        """Check a single subdomain for SaaS patterns"""
        try:
            # Check CNAME records
            resolver = dns.resolver.Resolver()
            resolver.timeout = 5
            
            try:
                cname_answers = resolver.resolve(subdomain, 'CNAME')
                for answer in cname_answers:
                    cname = str(answer.target).lower()
                    
                    # Match against known SaaS patterns
                    for tool_name, tool_info in self.saas_patterns.items():
                        for pattern in tool_info['domains']:
                            if pattern in cname:
                                return {
                                    'tool': tool_name,
                                    'provider': tool_info['category'],
                                    'cname': cname,
                                    'subdomain': subdomain,
                                    'discovery_method': 'cname_record'
                                }
            except dns.resolver.NXDOMAIN:
                pass
            except Exception:
                pass
            
            # Check A records and HTTP response
            try:
                a_answers = resolver.resolve(subdomain, 'A')
                if a_answers:
                    # Try HTTP request to check for redirects or specific responses
                    http_info = await self._check_http_response(subdomain)
                    if http_info:
                        return http_info
            except Exception:
                pass
                
        except Exception:
            pass
        
        return None
    
    async def _check_http_response(self, subdomain: str) -> Optional[Dict]:
        """Check HTTP response for SaaS identification"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=10)) as session:
                # Try HTTPS first, then HTTP
                for protocol in ['https', 'http']:
                    url = f"{protocol}://{subdomain}"
                    try:
                        async with session.get(url, allow_redirects=True) as response:
                            if response.status == 200:
                                # Check response headers and content for SaaS indicators
                                headers = dict(response.headers)
                                content = await response.text()
                                
                                # Check for common SaaS indicators in headers
                                server = headers.get('server', '').lower()
                                if 'cloudflare' in server:
                                    return {
                                        'tool': 'cloudflare',
                                        'provider': 'Cloudflare',
                                        'subdomain': subdomain,
                                        'discovery_method': 'http_header',
                                        'details': {'server': server}
                                    }
                                
                                # Check for redirects to known SaaS providers
                                final_url = str(response.url).lower()
                                for tool_name, tool_info in self.saas_patterns.items():
                                    for domain in tool_info['domains']:
                                        if domain in final_url:
                                            return {
                                                'tool': tool_name,
                                                'provider': tool_info['category'],
                                                'subdomain': subdomain,
                                                'final_url': final_url,
                                                'discovery_method': 'http_redirect'
                                            }
                                
                                break  # If HTTPS works, don't try HTTP
                    except Exception:
                        continue
        except Exception:
            pass
        
        return None
    
    async def _check_ssl_certificates(self, domain: str) -> Dict[str, Any]:
        """Check SSL certificates for additional domain information"""
        discoveries = {}
        
        try:
            # Get SSL certificate info
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    # Check Subject Alternative Names for additional domains
                    san_domains = []
                    if 'subjectAltName' in cert:
                        for san_type, san_value in cert['subjectAltName']:
                            if san_type == 'DNS':
                                san_domains.append(san_value)
                    
                    # Check if any SAN domains match known SaaS patterns
                    for san_domain in san_domains:
                        for tool_name, tool_info in self.saas_patterns.items():
                            for pattern in tool_info['domains']:
                                if pattern in san_domain.lower():
                                    discoveries[f"ssl_{tool_name}"] = {
                                        'tool': tool_name,
                                        'provider': tool_info['category'],
                                        'san_domain': san_domain,
                                        'discovery_method': 'ssl_certificate'
                                    }
        except Exception as e:
            print(f"⚠️ Error checking SSL certificate for {domain}: {e}")
        
        return discoveries
    
    async def check_api_endpoints(self, tool_list: List[str]) -> Dict[str, Dict]:
        """Check API endpoints for tool version and status information"""
        cache_key = f"api_endpoints_{hash(tuple(sorted(tool_list)))}"
        cached_result = self._load_cache(cache_key)
        if cached_result:
            print("📋 Using cached API endpoint results")
            return cached_result
        
        print(f"🔍 Checking API endpoints for {len(tool_list)} tools")
        results = {}
        
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=15)) as session:
            tasks = []
            for tool in tool_list:
                if tool.lower() in self.saas_patterns:
                    tasks.append(self._check_single_api(session, tool))
            
            api_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for tool, result in zip(tool_list, api_results):
                if isinstance(result, dict) and result:
                    results[tool] = result
                elif not isinstance(result, Exception):
                    results[tool] = {
                        'status': 'no_api_check',
                        'discovery_method': 'api_probe'
                    }
        
        # Save to cache
        self._save_cache(cache_key, results)
        
        print(f"✅ API checks completed for {len(results)} tools")
        return results
    
    async def _check_single_api(self, session: aiohttp.ClientSession, tool: str) -> Optional[Dict]:
        """Check a single API endpoint"""
        tool_config = self.saas_patterns.get(tool.lower())
        if not tool_config:
            return None
        
        api_endpoint = tool_config['api_endpoint']
        
        try:
            # Try a basic API call (usually returns version info or requires auth)
            async with session.get(api_endpoint, allow_redirects=True) as response:
                result = {
                    'status_code': response.status,
                    'discovery_method': 'api_probe',
                    'api_endpoint': api_endpoint
                }
                
                if response.status == 200:
                    result['status'] = 'active'
                    # Try to extract version info from headers
                    if 'api-version' in response.headers:
                        result['api_version'] = response.headers['api-version']
                    if 'x-api-version' in response.headers:
                        result['api_version'] = response.headers['x-api-version']
                elif response.status == 401:
                    result['status'] = 'requires_auth'
                elif response.status == 403:
                    result['status'] = 'forbidden'
                else:
                    result['status'] = 'unreachable'
                
                return result
                
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'discovery_method': 'api_probe',
                'api_endpoint': api_endpoint
            }
    
    async def enhance_tool_inventory(self, existing_tools: Dict[str, dict], domain: str = None) -> Dict[str, dict]:
        """Enhance existing tool inventory with automated discovery"""
        print("🚀 Starting automated tool inventory enhancement")
        
        enhanced_inventory = existing_tools.copy()
        
        # Step 1: Domain-based discovery (if domain provided)
        if domain:
            domain_discoveries = await self.discover_domain_footprint(domain)
            
            # Add newly discovered tools
            for discovery_key, discovery_info in domain_discoveries.items():
                tool_name = discovery_info.get('tool', discovery_key)
                provider = discovery_info.get('provider', 'Unknown')
                
                if tool_name not in enhanced_inventory:
                    enhanced_inventory[tool_name] = {
                        'category': discovery_info.get('category', 'Auto-discovered'),
                        'version': 'unknown',
                        'users': ['auto-detected'],
                        'criticality': 'Unknown',
                        'discovery_method': discovery_info.get('discovery_method', 'domain_analysis'),
                        'discovery_details': discovery_info,
                        'provider': provider
                    }
                    print(f"📦 Auto-discovered: {tool_name} ({provider})")
        
        # Step 2: API-based enhancement for known tools
        tool_names = list(enhanced_inventory.keys())
        api_results = await self.check_api_endpoints(tool_names)
        
        # Enhance existing tools with API data
        for tool_name, api_data in api_results.items():
            if tool_name in enhanced_inventory:
                enhanced_inventory[tool_name].update(api_data)
                if api_data.get('api_version'):
                    enhanced_inventory[tool_name]['version'] = api_data['api_version']
                print(f"🔄 Enhanced: {tool_name} (API status: {api_data.get('status', 'unknown')})")
        
        # Step 3: Add discovery timestamp
        for tool_name, tool_data in enhanced_inventory.items():
            if 'last_discovery' not in tool_data:
                tool_data['last_discovery'] = datetime.now().isoformat()
        
        print(f"✅ Enhanced inventory: {len(enhanced_inventory)} tools total")
        return enhanced_inventory
    
    def get_discovery_summary(self, enhanced_inventory: Dict[str, dict]) -> Dict[str, Any]:
        """Generate a summary of discovery results"""
        total_tools = len(enhanced_inventory)
        auto_discovered = len([t for t in enhanced_inventory.values() if 'auto-discovered' in t.get('category', '').lower()])
        api_enhanced = len([t for t in enhanced_inventory.values() if 'api_probe' in t.get('discovery_method', '')])
        
        discovery_methods = {}
        categories = {}
        
        for tool_data in enhanced_inventory.values():
            # Count discovery methods
            method = tool_data.get('discovery_method', 'manual')
            discovery_methods[method] = discovery_methods.get(method, 0) + 1
            
            # Count categories
            category = tool_data.get('category', 'Unknown')
            categories[category] = categories.get(category, 0) + 1
        
        return {
            'total_tools': total_tools,
            'auto_discovered': auto_discovered,
            'api_enhanced': api_enhanced,
            'discovery_methods': discovery_methods,
            'categories': categories,
            'discovery_timestamp': datetime.now().isoformat()
        }

# Convenience functions
async def quick_domain_discovery(domain: str) -> Dict[str, Any]:
    """Quick domain discovery for testing"""
    engine = DiscoveryEngine()
    return await engine.discover_domain_footprint(domain)

async def enhance_existing_inventory(tools: Dict[str, dict], domain: str = None) -> Tuple[Dict[str, dict], Dict[str, Any]]:
    """Enhance existing tool inventory and return summary"""
    engine = DiscoveryEngine()
    enhanced = await engine.enhance_tool_inventory(tools, domain)
    summary = engine.get_discovery_summary(enhanced)
    return enhanced, summary
import json
import urllib.request

payload = {
    'question': 'Explain this repository',
    'analysis': {
        'repository': {'name': 'atlas', 'full_name': 'example/atlas', 'owner': 'example', 'description': 'repo analysis platform', 'topics': ['ai']},
        'summary': {'overview': 'Repository analysis platform', 'purpose': 'Help understand codebases', 'current_status': 'healthy', 'highlights': ['rich analysis']},
        'tech_stack': {'languages': ['Python'], 'frontend': ['React'], 'backend': ['FastAPI'], 'database': ['PostgreSQL'], 'cloud': ['Azure'], 'ci_cd': ['GitHub Actions'], 'package_managers': ['npm'], 'containers': ['Docker'], 'mobile': []},
        'architecture': {'style': 'modular monolith', 'confidence': 0.8, 'architecture_patterns': [{'name': 'layered', 'confidence': 0.9, 'evidence': []}], 'deployment': ['containerized'], 'modules': ['backend', 'frontend'], 'organization': ['services', 'components'], 'summary': 'Layered application'},
        'structure': {'summary': 'Backend and frontend separated', 'major_folders': ['backend', 'src'], 'entry_points': ['main.py', 'src/main.tsx'], 'configuration_files': ['package.json', 'requirements.txt']},
        'health': {'score': 79, 'overall_status': 'good', 'checks': {}, 'missing_recommendations': []},
        'activity': {'stars': 100, 'forks': 10, 'open_issues': 5, 'recent_commits': 12, 'recent_pull_requests': 3, 'releases': 2, 'activity_level': 'active', 'maintenance_status': 'healthy', 'repository_maturity': 'maturing'},
        'classification': {'project_type': 'Application', 'primary_classification': 'Developer tool'}
    }
}

data = json.dumps(payload).encode()
req = urllib.request.Request('http://127.0.0.1:8000/chat', data=data, headers={'Content-Type': 'application/json'}, method='POST')
with urllib.request.urlopen(req, timeout=30) as resp:
    print(resp.read().decode())

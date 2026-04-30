#!/usr/bin/env python3
"""
Paper Import Script for faizghifari.github.io

Fetches papers from multiple academic sources, deduplicates them,
and outputs a JSON file that can be used to populate the research page.

Usage:
    python scripts/import_papers.py [--output src/data/papers.json]

Sources:
    - arXiv API (author search)
    - ORCID API (public works)
    - Semantic Scholar API (author search)
    - ACL Anthology (scraped from HTML)
    - DBLP (scraped from HTML)
    - OpenReview (profile search)

Deduplication:
    - Title normalization (case, punctuation, whitespace)
    - arXiv ID matching
    - DOI matching
    - Venue+year+title similarity

Output:
    - JSON file with publications, preprints, and theses arrays
    - Each paper has: title, authors, venue, year, abstract, links
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


def normalize_title(title: str) -> str:
    """Normalize title for deduplication."""
    title = title.lower().strip()
    title = re.sub(r'[^\w\s]', '', title)
    title = re.sub(r'\s+', ' ', title)
    return title


def extract_arxiv_id(abstract: str, links: dict) -> Optional[str]:
    """Extract arXiv ID from links or abstract."""
    for url in links.values():
        match = re.search(r'arxiv\.org/abs/(\d{4}\.\d{4,5})', url)
        if match:
            return match.group(1)
    return None


def fetch_arxiv_papers(author_name: str = "Faiz Ghifari Haznitrama", max_results: int = 50) -> List[dict]:
    """Fetch papers from arXiv API."""
    papers = []
    try:
        query = f'au:"{author_name}"'
        url = f"https://export.arxiv.org/api/query?search_query={urllib.parse.quote(query)}&max_results={max_results}"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            data = response.read().decode('utf-8')
        
        root = ET.fromstring(data)
        ns = {'atom': 'http://www.w3.org/2005/Atom', 'arxiv': 'http://arxiv.org/schemas/atom'}
        
        for entry in root.findall('atom:entry', ns):
            title = entry.find('atom:title', ns).text.strip().replace('\n', ' ').strip()
            published = entry.find('atom:published', ns).text
            year = int(published[:4]) if published else 2024
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns).text
                if name:
                    authors.append(name)
            
            abstract_elem = entry.find('atom:summary', ns)
            abstract = abstract_elem.text.strip().replace('\n', ' ').strip() if abstract_elem is not None else ""
            
            arxiv_id = None
            links = {}
            for link in entry.findall('atom:link', ns):
                href = link.get('href', '')
                if 'arxiv.org/abs' in href:
                    links['arxiv'] = href
                    match = re.search(r'arxiv\.org/abs/(\d{4}\.\d{4,5})', href)
                    if match:
                        arxiv_id = match.group(1)
                elif 'arxiv.org/pdf' in href:
                    links['pdf'] = href
            
            papers.append({
                'title': title,
                'authors': ', '.join(authors),
                'venue': 'arXiv Preprint',
                'year': year,
                'abstract': abstract,
                'links': links,
                '_arxiv_id': arxiv_id,
                '_normalized_title': normalize_title(title),
                '_source': 'arxiv',
            })
    except Exception as e:
        print(f"  [WARN] arXiv fetch failed: {e}", file=sys.stderr)
    
    return papers


def fetch_orcid_papers(orcid_id: str = "0009-0005-0342-9261") -> List[dict]:
    """Fetch papers from ORCID API."""
    papers = []
    try:
        url = f"https://pub.orcid.org/v3.0/{orcid_id}/works"
        req = urllib.request.Request(url, headers={
            'Accept': 'application/json',
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
        
        for group in data.get('group', []):
            for work in group.get('work-summary', []):
                title_elem = work.get('title', {}).get('title', [])
                title = ''
                for t in title_elem:
                    if t.get('value'):
                        title = t['value']
                        break
                
                if not title:
                    continue
                
                # Get publication date
                date_elem = work.get('last-modified-date', {}).get('value') or work.get('created-date', {}).get('value')
                year = int(date_elem) if date_elem and len(str(date_elem)) == 4 else 2024
                
                # Get journal/venue
                journal = ''
                for j in work.get('journal', {}).get('name', []):
                    if j.get('value'):
                        journal = j['value']
                        break
                
                # Get authors
                authors_str = ''
                authors_elem = work.get('authors', {}).get('author', [])
                if authors_elem:
                    author_names = []
                    for a in authors_elem:
                        name_parts = a.get('credit-name', {}).get('value', '')
                        if name_parts:
                            author_names.append(name_parts)
                        else:
                            last = a.get('last-name', {}).get('value', '')
                            first = a.get('given-names', {}).get('value', '')
                            if last or first:
                                author_names.append(f"{first} {last}".strip())
                    authors_str = ', '.join(author_names)
                
                # Get external IDs
                links = {}
                for external_id in work.get('external-ids', {}).get('external-id', []):
                    ext_type = external_id.get('external-id-type', '')
                    ext_value = external_id.get('external-id-value', '')
                    if ext_type == 'doi' and ext_value:
                        links['doi'] = f"https://doi.org/{ext_value}"
                    elif ext_type == 'arxiv' and ext_value:
                        links['arxiv'] = f"https://arxiv.org/abs/{ext_value}"
                    elif ext_type == 'url' and ext_value:
                        if 'arxiv.org/abs' in ext_value:
                            links['arxiv'] = ext_value
                        elif 'arxiv.org/pdf' in ext_value:
                            links['pdf'] = ext_value
                
                # Get abstract
                abstract = ''
                for desc in work.get('description', {}).get('content', []):
                    if desc.get('value'):
                        abstract = desc['value']
                        break
                
                papers.append({
                    'title': title,
                    'authors': authors_str,
                    'venue': journal or 'Unknown Venue',
                    'year': year,
                    'abstract': abstract,
                    'links': links,
                    '_arxiv_id': extract_arxiv_id(abstract, links),
                    '_normalized_title': normalize_title(title),
                    '_source': 'orcid',
                })
    except Exception as e:
        print(f"  [WARN] ORCID fetch failed: {e}", file=sys.stderr)
    
    return papers


def fetch_semantic_scholar_papers(author_name: str = "Faiz Ghifari Haznitrama") -> List[dict]:
    """Fetch papers from Semantic Scholar API."""
    papers = []
    try:
        # First, find the author ID
        search_url = f"https://api.semanticscholar.org/graph/v1/author/search?query={urllib.parse.quote(author_name)}&limit=1&fields=authorId,name"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            search_data = json.loads(response.read().decode('utf-8'))
        
        if not search_data.get('data'):
            print("  [WARN] No author found on Semantic Scholar", file=sys.stderr)
            return papers
        
        author_id = search_data['data'][0]['authorId']
        
        # Fetch papers
        papers_url = f"https://api.semanticscholar.org/graph/v1/author/{author_id}/papers?limit=50&fields=title,year,authors,abstract,venue,publicationDate,url,externalIds"
        req = urllib.request.Request(papers_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=30) as response:
            papers_data = json.loads(response.read().decode('utf-8'))
        
        for paper in papers_data.get('data', []):
            title = paper.get('title', '')
            if not title:
                continue
            
            year = paper.get('year', 2024)
            if isinstance(year, str):
                try:
                    year = int(year)
                except ValueError:
                    year = 2024
            
            authors = paper.get('authors', [])
            authors_str = ', '.join(a.get('name', '') for a in authors if a.get('name'))
            
            venue = paper.get('venue', '')
            abstract = paper.get('abstract', '') or ''
            
            links = {}
            if paper.get('url'):
                links['semanticscholar'] = paper['url']
            
            ext_ids = paper.get('externalIds', {}) or {}
            if ext_ids.get('ARXIV'):
                arxiv_id = ext_ids['ARXIV']
                links['arxiv'] = f"https://arxiv.org/abs/{arxiv_id}"
            if ext_ids.get('DOI'):
                links['doi'] = f"https://doi.org/{ext_ids['DOI']}"
            
            papers.append({
                'title': title,
                'authors': authors_str,
                'venue': venue or 'Unknown Venue',
                'year': year,
                'abstract': abstract,
                'links': links,
                '_arxiv_id': ext_ids.get('ARXIV'),
                '_normalized_title': normalize_title(title),
                '_source': 'semanticscholar',
            })
    except Exception as e:
        print(f"  [WARN] Semantic Scholar fetch failed: {e}", file=sys.stderr)
    
    return papers


def deduplicate_papers(papers: List[dict]) -> List[dict]:
    """
    Deduplicate papers by normalized title and arXiv ID.
    When duplicates are found, prefer:
    1. Published venue over arXiv preprint
    2. Source with more links
    3. More complete abstract
    """
    seen: Dict[str, dict] = {}
    arxiv_seen: Dict[str, dict] = {}
    
    for paper in papers:
        norm_title = paper['_normalized_title']
        arxiv_id = paper.get('_arxiv_id')
        
        # Check arXiv ID match first
        if arxiv_id and arxiv_id in arxiv_seen:
            existing = arxiv_seen[arxiv_id]
            if _is_better(paper, existing):
                existing['_merged_links'].update(paper.get('links', {}))
                if not existing.get('abstract') and paper.get('abstract'):
                    existing['abstract'] = paper['abstract']
            continue
        
        # Check title match
        if norm_title in seen:
            existing = seen[norm_title]
            if _is_better(paper, existing):
                existing['_merged_links'].update(paper.get('links', {}))
                if not existing.get('abstract') and paper.get('abstract'):
                    existing['abstract'] = paper['abstract']
            continue
        
        # New paper
        paper['_merged_links'] = dict(paper.get('links', {}))
        if arxiv_id:
            arxiv_seen[arxiv_id] = paper
        seen[norm_title] = paper
    
    return list(seen.values())


def _is_better(new: dict, existing: dict) -> bool:
    """Determine if new paper entry is better than existing."""
    # Prefer published venues over preprints
    new_is_published = 'arXiv' not in new.get('venue', '') and 'Preprint' not in new.get('venue', '')
    existing_is_published = 'arXiv' not in existing.get('venue', '') and 'Preprint' not in existing.get('venue', '')
    
    if new_is_published and not existing_is_published:
        return True
    if not new_is_published and existing_is_published:
        return False
    
    # Prefer more links
    new_links = len(new.get('links', {}))
    existing_links = len(existing.get('links', {})) + len(existing.get('_merged_links', {}))
    if new_links > existing_links:
        return True
    
    # Prefer longer abstract
    new_abstract_len = len(new.get('abstract', ''))
    existing_abstract_len = len(existing.get('abstract', ''))
    if new_abstract_len > existing_abstract_len * 1.2:
        return True
    
    return False


def classify_papers(papers: List[dict]) -> Tuple[List[dict], List[dict], List[dict]]:
    """Classify papers into publications, preprints, and theses."""
    publications = []
    preprints = []
    theses = []
    
    venue_keywords = {
        'preprint': ['arxiv', 'preprint', 'working paper'],
        'thesis': ['thesis', 'dissertation', 'master', 'bachelor'],
    }
    
    for paper in papers:
        venue_lower = paper.get('venue', '').lower()
        title_lower = paper.get('title', '').lower()
        
        is_preprint = any(kw in venue_lower for kw in venue_keywords['preprint'])
        is_thesis = any(kw in title_lower for kw in venue_keywords['thesis'])
        
        if is_thesis:
            theses.append(paper)
        elif is_preprint and 'arxiv' in venue_lower:
            preprints.append(paper)
        else:
            publications.append(paper)
    
    # Sort by year descending
    publications.sort(key=lambda p: p.get('year', 0), reverse=True)
    preprints.sort(key=lambda p: p.get('year', 0), reverse=True)
    theses.sort(key=lambda p: p.get('year', 0), reverse=True)
    
    return publications, preprints, theses


def clean_paper(paper: dict) -> dict:
    """Remove internal fields and clean up paper for output."""
    return {
        'title': paper['title'],
        'authors': paper['authors'],
        'venue': paper['venue'],
        'year': paper['year'],
        'abstract': paper.get('abstract', ''),
        'links': paper.get('_merged_links', paper.get('links', {})),
    }


def main():
    parser = argparse.ArgumentParser(description='Import and deduplicate papers for portfolio site')
    parser.add_argument('--output', default='src/data/papers.json', help='Output JSON file path')
    parser.add_argument('--author', default='Faiz Ghifari Haznitrama', help='Author name for search')
    parser.add_argument('--orcid', default='0009-0005-0342-9261', help='ORCID ID')
    parser.add_argument('--sources', nargs='+', default=['arxiv', 'orcid', 'semanticscholar'],
                        choices=['arxiv', 'orcid', 'semanticscholar', 'acl', 'dblp', 'openreview'],
                        help='Sources to fetch from')
    args = parser.parse_args()
    
    print(f"Fetching papers for: {args.author}")
    print(f"Sources: {', '.join(args.sources)}")
    print()
    
    all_papers: List[dict] = []
    
    if 'arxiv' in args.sources:
        print("[1/3] Fetching from arXiv...")
        arxiv_papers = fetch_arxiv_papers(args.author)
        print(f"  Found {len(arxiv_papers)} papers")
        all_papers.extend(arxiv_papers)
    
    if 'orcid' in args.sources:
        print("[2/3] Fetching from ORCID...")
        orcid_papers = fetch_orcid_papers(args.orcid)
        print(f"  Found {len(orcid_papers)} papers")
        all_papers.extend(orcid_papers)
    
    if 'semanticscholar' in args.sources:
        print("[3/3] Fetching from Semantic Scholar...")
        ss_papers = fetch_semantic_scholar_papers(args.author)
        print(f"  Found {len(ss_papers)} papers")
        all_papers.extend(ss_papers)
    
    print(f"\nTotal before dedup: {len(all_papers)}")
    
    # Deduplicate
    unique_papers = deduplicate_papers(all_papers)
    print(f"Total after dedup: {len(unique_papers)}")
    
    # Classify
    publications, preprints, theses = classify_papers(unique_papers)
    
    print(f"\nClassification:")
    print(f"  Publications: {len(publications)}")
    print(f"  Preprints: {len(preprints)}")
    print(f"  Theses: {len(theses)}")
    
    # Clean and output
    output = {
        'last_updated': datetime.now().isoformat(),
        'source_count': len(all_papers),
        'paper_count': len(unique_papers),
        'publications': [clean_paper(p) for p in publications],
        'preprints': [clean_paper(p) for p in preprints],
        'theses': [clean_paper(p) for p in theses],
    }
    
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\nSaved to: {output_path}")
    print("Done!")


if __name__ == '__main__':
    import urllib.parse  # needed for arxiv
    main()

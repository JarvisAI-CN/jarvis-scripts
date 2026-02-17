#!/usr/bin/env python3
"""
扫描工作区中的所有飞书文档链接
提取文档 token 和相关信息
"""

import os
import re
from pathlib import Path
from typing import List, Dict

def scan_workspace_for_feishu_docs(workspace_path: str) -> List[Dict]:
    """
    扫描工作区，查找所有飞书文档链接
    """
    feishu_docs = []
    
    # 飞书文档链接的正则表达式
    patterns = [
        r'https://[a-z0-9-]+\.feishu\.cn/docx/([a-zA-Z0-9]+)',
        r'https://[a-z0-9-]+\.feishu\.cn/wiki/([a-zA-Z0-9]+)',
        r'docx/([a-zA-Z0-9]+)',
        r'wiki/([a-zA-Z0-9]+)',
    ]
    
    combined_pattern = '|'.join(f'({p})' for p in patterns)
    
    # 遍历工作区
    for root, dirs, files in os.walk(workspace_path):
        # 跳过隐藏目录和特定目录
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', '__pycache__', '.git']]
        
        for file in files:
            if not file.endswith('.md'):
                continue
                
            file_path = os.path.join(root, file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # 查找所有匹配的链接
                matches = re.finditer(combined_pattern, content)
                
                for match in matches:
                    # 提取 token
                    token = None
                    for group in match.groups():
                        if group and len(group) > 5 and re.match(r'^[a-zA-Z0-9]+$', group):
                            token = group
                            break
                    
                    if token:
                        feishu_docs.append({
                            'token': token,
                            'file': file_path.replace(workspace_path, ''),
                            'link': match.group(0)
                        })
                        
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
    
    return feishu_docs

def main():
    workspace = '/home/ubuntu/.openclaw/workspace'
    
    print("🔍 扫描工作区中的飞书文档...")
    docs = scan_workspace_for_feishu_docs(workspace)
    
    if not docs:
        print("❌ 未找到任何飞书文档")
        return
    
    # 去重
    unique_docs = {}
    for doc in docs:
        token = doc['token']
        if token not in unique_docs:
            unique_docs[token] = doc
        else:
            # 记录重复引用
            unique_docs[token]['file'] += f", {doc['file']}"
    
    print(f"\n✅ 找到 {len(unique_docs)} 个唯一的飞书文档:\n")
    
    for i, (token, doc) in enumerate(unique_docs.items(), 1):
        print(f"{i}. Token: {token}")
        print(f"   引用位置: {doc['file']}")
        print(f"   链接: {doc['link'][:80]}..." if len(doc['link']) > 80 else f"   链接: {doc['link']}")
        print()
    
    # 保存到文件
    output_file = '/home/ubuntu/.openclaw/workspace/feishu_docs_inventory.json'
    import json
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_docs, f, ensure_ascii=False, indent=2)
    
    print(f"📋 清单已保存到: {output_file}")

if __name__ == '__main__':
    main()

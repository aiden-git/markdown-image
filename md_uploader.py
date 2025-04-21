import os
import re
import json
import base64
import argparse
import logging
from datetime import datetime
from pathlib import Path
import requests

# 日志配置
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('upload.log'),
        logging.StreamHandler()
    ]
)

class GithubUploader:
    def __init__(self, config):
        self.config = config
        self.upload_cache = {}

    def _gen_cloud_path(self, img_name, md_file_name=None):
        """生成云端存储路径"""
        # 以md文件名（不含扩展名）为目录
        if md_file_name:
            md_base = Path(md_file_name).stem
            return f"{self.config['save_dir']}/{md_base}/{img_name}"
        else:
            return f"{self.config['save_dir']}/{img_name}"

    def upload(self, img_path, md_file_name=None):
        """核心上传方法"""
        if img_path in self.upload_cache:
            return self.upload_cache[img_path]

        try:
            with open(img_path, 'rb') as f:
                content = base64.b64encode(f.read()).decode()

            cloud_path = self._gen_cloud_path(Path(img_path).name, md_file_name)
            api_url = f"https://api.github.com/repos/{self.config['owner']}/{self.config['repo']}/contents/{cloud_path}"
            headers = {"Authorization": f"token {self.config['token']}"}
            
            params = {
                "message": "auto upload by MD tool",
                "content": content,
                "branch": self.config['branch']
            }

            # 检查文件是否已存在，若存在则获取 sha
            check_url = api_url + f"?ref={self.config['branch']}"
            check_res = requests.get(check_url, headers=headers)
            logging.info(f"Check file response: {check_res.text}")
            if check_res.status_code == 200:
                check_json = check_res.json()
                if isinstance(check_json, dict):
                    sha = check_json.get('sha')
                    logging.info(f"sha value: {sha}")
                    if sha:
                        params["sha"] = sha

            res = requests.put(api_url, headers=headers, json=params)
            try:
                res.raise_for_status()
            except Exception as e:
                logging.error(f"Upload failed: {img_path} - {str(e)} - {res.text}")
                return None

            img_url = f"https://raw.githubusercontent.com/{self.config['owner']}/{self.config['repo']}/{self.config['branch']}/{cloud_path}"
            self.upload_cache[img_path] = img_url
            return img_url
        except Exception as e:
            logging.error(f"Upload failed: {img_path} - {str(e)}")
            return None

class MarkdownProcessor:
    def __init__(self, uploader):
        self.uploader = uploader
        self.pattern = re.compile(r'!\[.*?\]\((.*?)\)')

    def _backup_file(self, path):
        """创建备份文件"""
        backup = str(path) + ".bak"
        if not Path(backup).exists():
            Path(path).rename(backup)
        return backup

    def process(self, md_file):
        """处理单个Markdown文件"""
        try:
            md_path = Path(md_file)
            with open(md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            updates = []
            base_dir = md_path.parent

            for match in self.pattern.finditer(content):
                img_rel = match.group(1)
                if img_rel.startswith('http'): continue

                img_abs = (base_dir / img_rel).resolve()
                if not img_abs.exists():
                    logging.warning(f"Missing image: {img_abs}")
                    continue

                if (new_url := self.uploader.upload(str(img_abs), md_file_name=str(md_path))):
                    old_md = match.group(0)
                    new_md = old_md.replace(img_rel, new_url)
                    updates.append((old_md, new_md))

            if updates:
                self._backup_file(md_path)
                for old, new in updates:
                    content = content.replace(old, new)
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                logging.info(f"Updated: {md_path} ({len(updates)} images)")
            return True
        except Exception as e:
            logging.error(f"Process failed: {md_file} - {str(e)}")
            return False

def main():
    parser = argparse.ArgumentParser(description='Markdown图片批量上传工具')
    parser.add_argument('target', help='Markdown文件或目录路径')
    parser.add_argument('-r', '--recursive', action='store_true', help='递归处理子目录')
    args = parser.parse_args()

    # 加载配置
    try:
        with open('config.json') as f:
            config = json.load(f)
    except Exception as e:
        logging.error(f"Config error: {str(e)}")
        return

    uploader = GithubUploader(config)
    processor = MarkdownProcessor(uploader)

    target = Path(args.target)
    processed = 0

    try:
        if target.is_file():
            if processor.process(target):
                processed += 1
        elif target.is_dir():
            glob_pattern = '**/*.md' if args.recursive else '*.md'
            for md_file in target.glob(glob_pattern):
                if processor.process(md_file):
                    processed += 1
        logging.info(f"处理完成！成功更新 {processed} 个文件")
    except KeyboardInterrupt:
        logging.warning("操作被用户中断")

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
论文Markdown文件清洗脚本
功能：
1. 删除"摘要"二字前的所有内容
2. 删除英文摘要和英文关键词的所有内容
3. 保留中文摘要、中文关键词及正文内容
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple


class PaperCleaner:
    """论文清洗器"""
    
    def __init__(self, input_dir: str, output_dir: str):
        """
        初始化清洗器
        
        Args:
            input_dir: 输入目录路径
            output_dir: 输出目录路径
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        
        # 参考文献的正则表达式
        self.references_pattern = re.compile(
            r'(?:^|\n)#\s*(?:\[?参考文献\]?|References|参考资料|REFERENCES)(?:\s*[:：]?|\s*（References）).*?(?=\Z)',
            re.DOTALL | re.IGNORECASE
        )
        
    def clean_paper_content(self, content: str) -> str:
        """
        清洗论文内容
        
        Args:
            content: 原始论文内容
            
        Returns:
            清洗后的论文内容
        """
        # 1. 删除摘要之前的内容（如果有摘要的话）
        content = self._remove_content_before_abstract(content)
        
        # 2. 删除英文摘要和关键词
        content = self._remove_english_sections(content)
        
        # 3. 删除参考文献
        content = self.references_pattern.sub('', content)
        
        # 4. 清理多余的空行
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)
        
        return content.strip()
    
    def _remove_content_before_abstract(self, content: str) -> str:
        """
        删除摘要之前的所有内容，如果没有摘要则保留原内容
        
        Args:
            content: 原始内容
            
        Returns:
            处理后的内容
        """
        # 查找"摘要"的位置
        abstract_match = re.search(r'摘要', content)
        if abstract_match:
            return content[abstract_match.start():]
        else:
            # 如果没有找到"摘要"，检查是否是新闻类文章或其他类型
            # 保留原内容，但仍然进行其他清洗步骤
            return content
    
    def _remove_english_sections(self, content: str) -> str:
        """
        删除英文摘要和关键词部分
        
        Args:
            content: 原始内容
            
        Returns:
            处理后的内容
        """
        lines = content.split('\n')
        cleaned_lines = []
        
        # 标记是否在英文摘要/关键词区域
        in_english_section = False
        
        for line in lines:
            line_stripped = line.strip()
            
            # 检查是否进入英文摘要区域
            if (line_stripped.startswith('Abstract') or 
                line_stripped.startswith('ABSTRACT') or
                line_stripped == 'Abstract' or 
                line_stripped == 'ABSTRACT'):
                in_english_section = True
                continue
                
            # 检查是否进入英文关键词区域
            if (line_stripped.startswith('Key words') or 
                line_stripped.startswith('Keywords') or
                line_stripped.startswith('KEY WORDS') or
                line_stripped.startswith('KEYWORDS')):
                in_english_section = True
                continue
                
            # 检查是否结束英文区域，进入正文
            if in_english_section:
                # 如果遇到中文内容或明显的章节标题，说明英文区域结束
                if (self._is_chinese_content(line_stripped) or
                    line_stripped.startswith('#') or
                    re.match(r'^\d+\s', line_stripped) or  # 数字开头的章节
                    line_stripped.startswith('引言') or
                    line_stripped.startswith('1') or
                    line_stripped.startswith('一、') or
                    line_stripped.startswith('第一') or
                    '引言' in line_stripped):
                    in_english_section = False
                    cleaned_lines.append(line)
                    continue
                else:
                    # 仍在英文区域，跳过
                    continue
            
            # 如果不在英文区域，保留内容
            if not in_english_section:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def _is_chinese_content(self, text: str) -> bool:
        """
        判断文本是否包含中文内容
        
        Args:
            text: 待检查的文本
            
        Returns:
            是否包含中文
        """
        chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
        return bool(chinese_pattern.search(text))
    
    def clean_single_file(self, input_file: Path, output_file: Path) -> bool:
        """
        清洗单个文件
        
        Args:
            input_file: 输入文件路径
            output_file: 输出文件路径
            
        Returns:
            是否成功清洗
        """
        try:
            # 读取原文件
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 清洗内容
            cleaned_content = self.clean_paper_content(content)
            
            # 如果清洗后内容为空或过短，保留原文件的标题部分
            if len(cleaned_content.strip()) < 50:
                # 尝试保留文件的前几行作为标题
                lines = content.split('\n')
                title_lines = []
                for line in lines[:10]:  # 取前10行
                    if line.strip():
                        title_lines.append(line)
                    if len(title_lines) >= 3:  # 保留前3个非空行
                        break
                if title_lines:
                    cleaned_content = '\n'.join(title_lines)
            
            # 确保输出目录存在
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # 写入清洗后的内容
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(cleaned_content)
            
            print(f"✓ 已清洗: {input_file.name}")
            return True
            
        except Exception as e:
            print(f"✗ 清洗失败 {input_file.name}: {str(e)}")
            return False
    
    def clean_category(self, category: str) -> Tuple[int, int]:
        """
        清洗指定类别的所有论文
        
        Args:
            category: 论文类别名称
            
        Returns:
            (成功数量, 总数量)
        """
        input_category_dir = self.input_dir / category
        output_category_dir = self.output_dir / category
        
        if not input_category_dir.exists():
            print(f"警告: 输入目录不存在: {input_category_dir}")
            return 0, 0
        
        # 获取所有md文件
        md_files = list(input_category_dir.glob("*.md"))
        
        # 过滤掉README文件
        md_files = [f for f in md_files if f.name.lower() != 'readme.md']
        
        success_count = 0
        total_count = len(md_files)
        
        print(f"\n开始清洗类别: {category} (共 {total_count} 个文件)")
        
        for md_file in md_files:
            output_file = output_category_dir / md_file.name
            if self.clean_single_file(md_file, output_file):
                success_count += 1
        
        print(f"类别 {category} 清洗完成: {success_count}/{total_count}")
        return success_count, total_count
    
    def clean_all_categories(self) -> None:
        """清洗所有类别的论文"""
        categories = ['others', 'priority_remaining', 'test']
        
        total_success = 0
        total_files = 0
        
        print("开始清洗所有论文...")
        print(f"输入目录: {self.input_dir}")
        print(f"输出目录: {self.output_dir}")
        
        for category in categories:
            success, total = self.clean_category(category)
            total_success += success
            total_files += total
        
        print(f"\n清洗完成!")
        print(f"总计: {total_success}/{total_files} 个文件成功清洗")
        
        if total_success < total_files:
            print(f"有 {total_files - total_success} 个文件清洗失败，请检查日志")


def main():
    """主函数"""
    # 设置输入和输出目录
    input_dir = r"E:\langchain\data\raw\papers"
    output_dir = r"E:\langchain\data\processed\papers"
    
    # 创建清洗器
    cleaner = PaperCleaner(input_dir, output_dir)
    
    # 执行清洗
    cleaner.clean_all_categories()


if __name__ == "__main__":
    main()
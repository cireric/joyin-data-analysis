#!/usr/bin/env python3
"""
单元测试 - PDF转Word工具
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

import pytest
from pdf2word import (
    parse_page_range, validate_input,
    InputFileNotFoundError, InvalidPDFError, InvalidPageRangeError
)


class TestValidateInput:
    """validate_input 测试"""
    
    def test_file_not_exists(self, tmp_path):
        """测试文件不存在"""
        with pytest.raises(InputFileNotFoundError):
            validate_input(str(tmp_path / 'notexist.pdf'))
    
    def test_not_pdf(self, tmp_path):
        """测试非PDF文件"""
        txt_file = tmp_path / 'test.txt'
        txt_file.write_text('test')
        with pytest.raises(InvalidPDFError):
            validate_input(str(txt_file))
    
    def test_valid_pdf(self, tmp_path):
        """测试有效PDF文件"""
        pdf_file = tmp_path / 'test.pdf'
        pdf_file.write_text('fake pdf')
        result = validate_input(str(pdf_file))
        assert result == pdf_file


class TestParsePageRange:
    """parse_page_range 测试"""
    
    def test_none_input(self):
        """测试空输入"""
        assert parse_page_range(None) is None
        assert parse_page_range('') is None
    
    def test_single_page(self):
        """测试单页"""
        assert parse_page_range('1') == [1]
        assert parse_page_range('5') == [5]
    
    def test_page_range(self):
        """测试页码范围"""
        assert parse_page_range('1-5') == [1, 2, 3, 4, 5]
        assert parse_page_range('10-12') == [10, 11, 12]
    
    def test_multiple_pages(self):
        """测试多个页码"""
        assert parse_page_range('1,3,5') == [1, 3, 5]
    
    def test_mixed_format(self):
        """测试混合格式"""
        assert parse_page_range('1-3,5,7-9') == [1, 2, 3, 5, 7, 8, 9]
    
    def test_sorted_output(self):
        """测试输出已排序"""
        assert parse_page_range('5,1,3') == [1, 3, 5]
    
    def test_invalid_format(self):
        """测试无效格式"""
        with pytest.raises(InvalidPageRangeError):
            parse_page_range('abc')
    
    def test_negative_page(self):
        """测试负数页码"""
        with pytest.raises(InvalidPageRangeError):
            parse_page_range('-1')
    
    def test_zero_page(self):
        """测试零页码"""
        with pytest.raises(InvalidPageRangeError):
            parse_page_range('0')
    
    def test_start_greater_than_end(self):
        """测试起始页大于结束页"""
        with pytest.raises(InvalidPageRangeError):
            parse_page_range('5-1')
    
    def test_whitespace_handling(self):
        """测试空格处理"""
        assert parse_page_range(' 1 - 5 ') == [1, 2, 3, 4, 5]
        assert parse_page_range('1, 3, 5') == [1, 3, 5]


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

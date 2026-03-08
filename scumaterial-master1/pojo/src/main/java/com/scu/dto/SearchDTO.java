package com.scu.dto;

import lombok.Data;
import java.util.List;

/**
 * 搜索请求DTO
 * 兼容旧项目的搜索API
 */
@Data
public class SearchDTO {
    /**
     * 第一级分类（如：骨诱导、类骨磷灰石、工艺优化、高通量实验）
     */
    private String select1;
    
    /**
     * 第二级分类（如：材料组成成分、基本物理性能等）
     */
    private String select2;
    
    /**
     * 搜索关键词
     */
    private String select3;
    
    /**
     * 要搜索的字段名列表（可选）
     */
    private List<String> select4;
}


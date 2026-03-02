package com.scu.mapper;


import org.apache.ibatis.annotations.MapKey;
import org.apache.ibatis.annotations.Mapper;
import org.apache.ibatis.annotations.Param;

import java.util.List;
import java.util.Map;

@Mapper
public interface TemplateDataMapper {

    //获取所有数据
    public List<Map<String,Object>> getAllTemplateData(@Param("templateId")Long templateId);
    //获取所有审核通过的数据
    public List<Map<String,Object>> getAuditedTemplateData(@Param("templateId")Long templateId);
    //获取所有未审核的数据（待审核）
    public List<Map<String,Object>> getUnAuditedTemplateData(@Param("templateId")Long templateId);

    //更新状态为审核通过
    boolean updateStatusToPass(@Param("templateId") Long templateId, @Param("templateDataId") List<Long> templateDataId);
    
    //更新状态为审核不通过
    boolean updateStatusToReject(@Param("templateId") Long templateId, @Param("templateDataId") List<Long> templateDataId);
}

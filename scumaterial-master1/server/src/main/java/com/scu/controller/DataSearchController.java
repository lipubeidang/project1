package com.scu.controller;

import com.scu.result.Result;
import com.scu.service.TemplateDataService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

/**
 * 数据检索Controller
 * 提供数据检索功能
 */
@RestController
@RequestMapping("/data/search")
@Tag(name = "数据检索", description = "数据检索相关接口")
public class DataSearchController {

    @Autowired
    private TemplateDataService templateDataService;

    /**
     * 在指定模板中搜索数据
     * @param templateId 模板ID
     * @param keyword 搜索关键词
     * @param fieldNames 要搜索的字段名列表（可选，为空则搜索所有字段）
     * @return 搜索结果
     */
    @Operation(summary = "在指定模板中搜索数据")
    @PostMapping("/query")
    public Result<List<Map<String, Object>>> searchData(
            @RequestParam Long templateId,
            @RequestParam String keyword,
            @RequestParam(required = false) List<String> fieldNames) {
        try {
            // 获取所有已审核的数据
            List<Map<String, Object>> allData = templateDataService.getAllAuditedTemplateData(templateId);
            
            if (allData == null || allData.isEmpty()) {
                return Result.success(new ArrayList<>());
            }

            // 如果指定了字段名，只在这些字段中搜索；否则在所有字段中搜索
            List<Map<String, Object>> results = allData.stream()
                    .filter(data -> {
                        if (fieldNames != null && !fieldNames.isEmpty()) {
                            // 在指定字段中搜索
                            return fieldNames.stream().anyMatch(fieldName -> {
                                Object value = data.get(fieldName);
                                return value != null && value.toString().toLowerCase().contains(keyword.toLowerCase());
                            });
                        } else {
                            // 在所有字段中搜索
                            return data.values().stream().anyMatch(value -> 
                                value != null && value.toString().toLowerCase().contains(keyword.toLowerCase())
                            );
                        }
                    })
                    .collect(Collectors.toList());

            return Result.success(results);
        } catch (Exception e) {
            return Result.error("搜索失败: " + e.getMessage());
        }
    }

    /**
     * 查询指定字段的数据
     * @param templateId 模板ID
     * @param fieldNames 要查询的字段名列表
     * @return 查询结果
     */
    @Operation(summary = "查询指定字段的数据")
    @PostMapping("/queryColumns")
    public Result<List<Map<String, Object>>> queryColumns(
            @RequestParam Long templateId,
            @RequestBody List<String> fieldNames) {
        try {
            List<Map<String, Object>> allData = templateDataService.getAllAuditedTemplateData(templateId);
            
            if (allData == null || allData.isEmpty()) {
                return Result.success(new ArrayList<>());
            }

            // 只返回指定字段的数据
            List<Map<String, Object>> results = allData.stream()
                    .map(data -> {
                        Map<String, Object> filtered = new java.util.HashMap<>();
                        fieldNames.forEach(fieldName -> {
                            if (data.containsKey(fieldName)) {
                                filtered.put(fieldName, data.get(fieldName));
                            }
                        });
                        return filtered;
                    })
                    .collect(Collectors.toList());

            return Result.success(results);
        } catch (Exception e) {
            return Result.error("查询失败: " + e.getMessage());
        }
    }

    /**
     * 多表联合查询（根据sampleSerial）
     * @param request 包含模板ID列表和sampleSerial的请求
     * @return 联合查询结果
     */
    @Operation(summary = "多表联合查询")
    @PostMapping("/dynamicJoin")
    public Result<List<Map<String, Object>>> dynamicJoinQuery(@RequestBody Map<String, Object> request) {
        try {
            @SuppressWarnings("unchecked")
            List<Long> templateIds = (List<Long>) request.get("templateIds");
            String sampleSerial = (String) request.get("sampleSerial");

            if (templateIds == null || templateIds.isEmpty() || sampleSerial == null) {
                return Result.error("参数不完整");
            }

            List<Map<String, Object>> results = new ArrayList<>();
            
            // 遍历所有模板，查找匹配sampleSerial的数据
            for (Long templateId : templateIds) {
                List<Map<String, Object>> data = templateDataService.getAllAuditedTemplateData(templateId);
                if (data != null) {
                    data.stream()
                            .filter(item -> sampleSerial.equals(item.get("sample_serial")) || 
                                          sampleSerial.equals(item.get("sampleSerial")))
                            .forEach(results::add);
                }
            }

            return Result.success(results);
        } catch (Exception e) {
            return Result.error("联合查询失败: " + e.getMessage());
        }
    }
}



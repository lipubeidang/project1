package com.scu.controller;

import com.scu.dto.SearchDTO;
import com.scu.service.LegacyDataSearchService;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

import java.util.*;

/**
 * 兼容旧项目的数据检索Controller
 * 提供与旧项目兼容的搜索API接口
 * 直接查询固定表结构的数据（不是模板数据）
 * 返回格式兼容旧项目的R类：code: 0 表示成功，code: 500 表示错误
 */
@RestController
@RequestMapping("/basemodule/search")
@Tag(name = "兼容搜索接口", description = "兼容旧项目的数据检索接口")
public class LegacySearchController {

    @Autowired
    private LegacyDataSearchService legacyDataSearchService;

    /**
     * 兼容旧项目的搜索接口
     * 直接查询固定表结构的数据（不是模板数据）
     * @param searchDTO 搜索请求参数
     * @return 搜索结果（兼容旧项目的R类格式）
     */
    @Operation(summary = "兼容旧项目的搜索接口")
    @PostMapping("/query")
    public Map<String, Object> searchAnyColumn(@RequestBody SearchDTO searchDTO) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            String select1 = searchDTO.getSelect1();
            String select2 = searchDTO.getSelect2();
            String select3 = searchDTO.getSelect3(); // 搜索关键词
            List<String> select4 = searchDTO.getSelect4(); // 要搜索的字段列表

            System.out.println("=== 收到搜索请求 ===");
            System.out.println("select1: " + select1);
            System.out.println("select2: " + select2);
            System.out.println("select3: " + select3);
            System.out.println("select4: " + select4);

            if (select1 == null) {
                result.put("code", 500);
                result.put("msg", "搜索参数不完整: select1 为空");
                return result;
            }

            // 根据 select1 和 select2 获取表名
            String tableName = legacyDataSearchService.getTableName(select1, select2);
            System.out.println("映射到的表名: " + tableName);
            
            if (tableName == null) {
                result.put("code", 500);
                result.put("msg", "表不存在! select1=" + select1 + ", select2=" + select2);
                return result;
            }

            // 在指定表中搜索数据（允许关键词为空，返回所有数据）
            List<Map<String, Object>> searchResults = legacyDataSearchService.searchInTable(
                tableName, 
                select3 != null ? select3.trim() : "", 
                select4
            );

            if (searchResults == null || searchResults.isEmpty()) {
                // 返回错误码 500 表示没有找到匹配记录（兼容旧项目）
                result.put("code", 500);
                result.put("msg", "没有找到匹配的记录");
                return result;
            }

            // 返回成功结果，code 为 0（兼容旧项目）
            result.put("code", 0);
            result.put("msg", "success");
            result.put("data", searchResults);
            return result;
        } catch (Exception e) {
            result.put("code", 500);
            result.put("msg", "搜索失败: " + e.getMessage());
            e.printStackTrace();
            return result;
        }
    }

    /**
     * 兼容旧项目的查询列接口
     * @param params 请求参数
     * @return 查询结果（兼容旧项目的R类格式）
     */
    @Operation(summary = "兼容旧项目的查询列接口")
    @PostMapping("/querycolums")
    public Map<String, Object> queryColumns(@RequestBody Map<String, Object> params) {
        Map<String, Object> result = new HashMap<>();
        
        try {
            String tableNameParam = (String) params.get("tableName");
            @SuppressWarnings("unchecked")
            List<String> fieldNames = (List<String>) params.get("fieldNames");
            String choice = (String) params.get("choice");

            if (tableNameParam == null || fieldNames == null || fieldNames.isEmpty()) {
                result.put("code", 500);
                result.put("msg", "参数不完整");
                return result;
            }

            // 根据 choice 和 tableName 获取实际表名
            String actualTableName = null;
            if (LegacyDataSearchService.MATERIAL_A.equals(choice)) {
                actualTableName = LegacyDataSearchService.TABLE_MAPPING_A.get(tableNameParam);
            } else if (LegacyDataSearchService.MATERIAL_B.equals(choice)) {
                actualTableName = LegacyDataSearchService.TABLE_MAPPING_B.get(tableNameParam);
            }

            if (actualTableName == null) {
                result.put("code", 0);
                result.put("msg", "success");
                result.put("data", null);
                return result;
            }

            // 查询指定字段的数据
            List<Map<String, Object>> allData = legacyDataSearchService.searchInTable(actualTableName, "", null);
            
            // 只返回指定字段
            List<Map<String, Object>> filteredResults = new ArrayList<>();
            for (Map<String, Object> row : allData) {
                Map<String, Object> filtered = new HashMap<>();
                for (String fieldName : fieldNames) {
                    if (row.containsKey(fieldName)) {
                        filtered.put(fieldName, row.get(fieldName));
                    }
                }
                if (!filtered.isEmpty()) {
                    filteredResults.add(filtered);
                }
            }

            result.put("code", 0);
            result.put("msg", "success");
            result.put("data", filteredResults);
            return result;
        } catch (Exception e) {
            result.put("code", 500);
            result.put("msg", "查询失败: " + e.getMessage());
            e.printStackTrace();
            return result;
        }
    }
}


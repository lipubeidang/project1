package com.scu.service;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

/**
 * 兼容旧项目的数据检索Service
 * 直接查询固定表结构的数据
 */
@Service
public class LegacyDataSearchService {

    private final JdbcTemplate jdbcTemplate;

    // 表名映射常量（与旧项目保持一致）
    public static final String MATERIAL_A = "类骨磷灰石";
    public static final String MATERIAL_B = "骨诱导";
    public static final String MATERIAL_C = "高通量实验";
    public static final String MATERIAL_D = "工艺优化";

    public static final Map<String, String> TABLE_MAPPING_A;
    public static final Map<String, String> TABLE_MAPPING_B;
    public static final Map<String, String> TABLE_MAPPING_C;
    public static final Map<String, String> TABLE_MAPPING_D;

    static {
        // 初始化 类骨磷灰石
        Map<String, String> mapA = new HashMap<>();
        mapA.put("材料表面性能", "材料表面性能表");
        mapA.put("基本物理性能", "基本物理性能表_new");
        mapA.put("体外表面形成", "体外类骨磷灰石形成表_体外类骨磷灰石形成_表面成分表");
        mapA.put("体外XRD", "体外类骨磷灰石形成表_体外类骨磷灰石形成_XRD");
        mapA.put("体外实验", "体外类骨磷灰石形成表_体外类骨磷灰石形成表");
        mapA.put("文献数据来源", "文献数据来源信息表");
        mapA.put("文献样品信息", "文献样品基本信息表");
        TABLE_MAPPING_A = Collections.unmodifiableMap(mapA);

        // 初始化 骨诱导
        Map<String, String> mapB = new HashMap<>();
        mapB.put("材料组成成分", "02_材料组成成分表");
        mapB.put("基本物理性能", "03_基本物理性能表");
        mapB.put("孔径相关性能", "04_孔径相关性能表");
        mapB.put("体内植入实验", "05_体内植入实验表");
        mapB.put("文献数据来源", "07_文献数据来源信息表");
        mapB.put("文献样品信息", "08_文献样品基本信息表");
        TABLE_MAPPING_B = Collections.unmodifiableMap(mapB);

        Map<String, String> mapC = new HashMap<>();
        mapC.put("体内", "hte_vivo");
        mapC.put("体外", "hte_vitro");
        TABLE_MAPPING_C = Collections.unmodifiableMap(mapC);

        Map<String, String> mapD = new HashMap<>();
        mapD.put("烧结工艺", "agglomerationprocess");
        mapD.put("几何结构", "geometry");
        mapD.put("力学性能评价", "mechanicalproperty");
        TABLE_MAPPING_D = Collections.unmodifiableMap(mapD);
    }

    public LegacyDataSearchService(JdbcTemplate jdbcTemplate) {
        this.jdbcTemplate = jdbcTemplate;
    }

    /**
     * 在指定表中搜索数据
     * @param tableName 表名
     * @param keyword 搜索关键词
     * @param columnNames 要搜索的列名列表（如果为空，则搜索所有列）
     * @return 搜索结果
     */
    public List<Map<String, Object>> searchInTable(String tableName, String keyword, List<String> columnNames) {
        try {
            System.out.println("=== 开始搜索 ===");
            System.out.println("表名: " + tableName);
            System.out.println("关键词: " + keyword);
            System.out.println("指定列: " + columnNames);
            
            // 首先检查表是否存在
            String checkTableSql = "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = ?";
            Integer tableExists = jdbcTemplate.queryForObject(checkTableSql, Integer.class, tableName);
            
            System.out.println("表存在检查结果: " + tableExists);
            
            if (tableExists == null || tableExists == 0) {
                System.err.println("表不存在: " + tableName);
                // 尝试列出所有表名，帮助调试
                try {
                    List<String> allTables = jdbcTemplate.queryForList(
                        "SELECT table_name FROM information_schema.tables WHERE table_schema = DATABASE()", 
                        String.class
                    );
                    System.out.println("数据库中的所有表: " + allTables);
                } catch (Exception e) {
                    System.err.println("获取表列表失败: " + e.getMessage());
                }
                return new ArrayList<>();
            }

            // 获取表的所有列名
            List<String> allColumns = getAllColumns(tableName);
            System.out.println("表的所有列: " + allColumns);
            
            if (allColumns.isEmpty()) {
                System.err.println("表 " + tableName + " 没有列");
                return new ArrayList<>();
            }

            // 如果关键词为空，返回所有数据
            if (keyword == null || keyword.trim().isEmpty()) {
                String sql = "SELECT * FROM `" + tableName + "`";
                System.out.println("执行SQL: " + sql);
                List<Map<String, Object>> allData = jdbcTemplate.queryForList(sql);
                System.out.println("查询到 " + allData.size() + " 条数据");
                return allData;
            }

            // 确定要搜索的列
            List<String> searchColumns = (columnNames != null && !columnNames.isEmpty()) 
                    ? columnNames.stream().filter(allColumns::contains).collect(Collectors.toList())
                    : allColumns;

            System.out.println("要搜索的列: " + searchColumns);

            if (searchColumns.isEmpty()) {
                System.err.println("没有可搜索的列");
                return new ArrayList<>();
            }

            // 构建搜索SQL - 使用 CONCAT_WS 连接所有列（与旧项目保持一致）
            StringBuilder sql = new StringBuilder("SELECT * FROM `").append(tableName).append("` WHERE ");
            
            if (columnNames != null && !columnNames.isEmpty()) {
                // 如果指定了列，使用 OR 连接
                sql.append("(");
                for (int i = 0; i < searchColumns.size(); i++) {
                    if (i > 0) {
                        sql.append(" OR ");
                    }
                    sql.append("`").append(searchColumns.get(i)).append("` LIKE ?");
                }
                sql.append(")");
            } else {
                // 如果没有指定列，使用 CONCAT_WS 连接所有列（与旧项目逻辑一致）
                String concatExpression = searchColumns.stream()
                        .map(col -> "IFNULL(`" + col + "`,'')")
                        .collect(Collectors.joining(", ", "CONCAT_WS('|', ", ")"));
                sql.append(concatExpression).append(" LIKE CONCAT('%', ?, '%')");
            }

            // 构建参数列表
            String likePattern = keyword;
            Object[] params;
            if (columnNames != null && !columnNames.isEmpty()) {
                params = new Object[searchColumns.size()];
                Arrays.fill(params, "%" + keyword + "%");
            } else {
                params = new Object[]{keyword};
            }

            System.out.println("执行SQL: " + sql.toString());
            System.out.println("参数: " + Arrays.toString(params));

            // 执行查询
            List<Map<String, Object>> results = jdbcTemplate.queryForList(sql.toString(), params);
            System.out.println("查询到 " + results.size() + " 条匹配数据");
            System.out.println("=== 搜索完成 ===");
            
            return results;
        } catch (Exception e) {
            System.err.println("查询表 " + tableName + " 失败: " + e.getMessage());
            e.printStackTrace();
            return new ArrayList<>();
        }
    }

    /**
     * 获取表的所有列名
     */
    private List<String> getAllColumns(String tableName) {
        try {
            String sql = "SELECT COLUMN_NAME FROM information_schema.COLUMNS WHERE table_schema = DATABASE() AND table_name = ? ORDER BY ORDINAL_POSITION";
            List<String> columns = jdbcTemplate.queryForList(sql, String.class, tableName);
            return columns != null ? columns : new ArrayList<>();
        } catch (Exception e) {
            System.err.println("获取表 " + tableName + " 的列名失败: " + e.getMessage());
            return new ArrayList<>();
        }
    }

    /**
     * 根据select1和select2获取表名
     */
    public String getTableName(String select1, String select2) {
        if (select1 == null || select2 == null) {
            return null;
        }

        if (MATERIAL_A.equals(select1)) {
            return TABLE_MAPPING_A.get(select2);
        } else if (MATERIAL_B.equals(select1)) {
            return TABLE_MAPPING_B.get(select2);
        } else if (MATERIAL_C.equals(select1)) {
            return TABLE_MAPPING_C.get(select2);
        } else if (MATERIAL_D.equals(select1)) {
            return TABLE_MAPPING_D.get(select2);
        }

        return null;
    }
}


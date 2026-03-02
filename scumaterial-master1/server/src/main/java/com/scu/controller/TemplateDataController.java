package com.scu.controller;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.scu.dto.FileMetaDto;
import com.scu.dto.TemplateDataDto;
import com.scu.result.Result;
import com.scu.service.TemplateDataService;
import jakarta.servlet.http.HttpServletResponse;
import io.swagger.v3.oas.annotations.parameters.RequestBody;
import io.swagger.v3.oas.annotations.Operation;
import io.swagger.v3.oas.annotations.Parameter;
import io.swagger.v3.oas.annotations.media.Content;
import io.swagger.v3.oas.annotations.media.Encoding;
import io.swagger.v3.oas.annotations.media.Schema;
import io.swagger.v3.oas.annotations.tags.Tag;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.MediaType;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/templateData")
@Tag(name = "模板数据相关接口",description = "指模板对应数据库表创建好之后，对该表的上传数据等操作")
public class TemplateDataController {

    @Autowired
    private TemplateDataService templateDataService;

    @Operation(summary = "添加模板数据单条方式")
    @PostMapping(value = "/addATemplateData")
    public Result addATemplateData_new ( @RequestPart("templateData") String templateData,
                                         @RequestPart(value = "files",required = false) List<MultipartFile> files) throws JsonProcessingException {
        templateDataService.saveTemplateDataSingle(templateData, files);
        return Result.success();
    }

    @PostMapping("/addTemplateDataBatch")
    public Result addTemplateDataBatchNew(@RequestPart("excel") MultipartFile excel, @RequestPart(value = "files",required = false) List<MultipartFile> files,@RequestParam("templateId") Long templateId) throws IOException {

        templateDataService.saveTemplateDataBatch(excel,files,templateId);

        return Result.success();
    }

    @Operation(summary = "获取指定模板的所有待审核数据",description = "获取指定模板的所有待审核数据")
    @GetMapping("/getTemplateData/{templateId}")
    public Result getTemplateData(@Parameter(description = "模板id") @PathVariable Long templateId){
//        String tableName="template_data_"+templateId;
        return null;
    }

    @Operation(summary = "获取所有模板数据")
    @GetMapping("/getAllTemplateData/{templateId}")
    public Result getAllTemplateData(@PathVariable("templateId") Long templateId){
        List<Map<String, Object>> allTemplateData = templateDataService.getAllTemplateData(templateId);
        return Result.success(allTemplateData);
    }

    @Operation(summary = "获取已审核通过的模板数据")
    @GetMapping("/getAuditedTemplateData/{templateId}")
    public Result getAuditedTemplateData(@PathVariable("templateId") Long templateId){
        List<Map<String, Object>> auditedTemplateData = templateDataService.getAllAuditedTemplateData(templateId);
        return Result.success(auditedTemplateData);
    }

    @Operation(summary = "获取文件")
    @GetMapping("/getFile/{fileId}")
    public void getFile(@PathVariable("fileId") String fileId, HttpServletResponse response){
        templateDataService.getFile(response, fileId);
    }

}

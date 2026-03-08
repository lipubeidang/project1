<template>
    <div>
        <!-- 导航栏 -->
        <Navbar @dropdown-action="handleDropdownAction" />

        <div class="content-wrapper">
            <div class="select-wrapper">
                <div class="select-data">
                    <span class="demonstration">1、请选择需要的数据</span>
                    <el-cascader :options="options_data" :props="props" clearable v-model="selectedValue"
                        :collapse-tags="true" style="width: 55%;" @change="processSelectedData"></el-cascader>
                    <span class="demonstration">2、请选择学习目标列</span>
                    <el-cascader :options="options_data" :props="props" clearable v-model="listValue"
                        :collapse-tags="true" style="width: 55%;"></el-cascader>
                    <span class="demonstration">3、请选择插值的方式</span>
                    <el-select v-model="value_insert" filterable placeholder="请选择" style="width: 55%;">
                        <el-option v-for="item in options_insert" :key="item.value" :label="item.label"
                            :value="item.value">
                        </el-option>
                    </el-select>
                </div>
                <div class="select-button">
                    <el-button type="primary" plain class="select_button" @click="fetchTableSelectData">确定</el-button>
                </div>
                <div class="separator"></div>
                <div class="select-model">
                    <span class="demonstration">请选择使用的模型</span>
                    <el-select v-model="value_model" filterable placeholder="请选择">
                        <el-option v-for="item in options_model" :key="item.value" :label="item.label"
                            :value="item.value">
                        </el-option>
                    </el-select>
                    <!-- 右侧图片和按钮区域 -->
                    <div class="image-button-wrap">
                        <!-- 图片区域 -->
                        <img src="../assets/mode.jpg" alt="示例图片" class="main-image">
                    </div>
                </div>
                <!-- 按钮区域 -->
                <!-- <div class="button-container"> -->
                <div class="select-button">
                    <el-button type="primary" @click="fetchTableResultData">运行模型</el-button>
                </div>
            </div>
            <div class="display-wrapper">
                <div class="display-select">
                    <div class="table-container" v-show="isTableShown">
                        <!-- 表格 -->
                        <el-table v-if="tableSelectData.length > 0 && tableSelectColumns.length > 0"
                            :data="tableSelectData" style="margin-top: 5px" max-height="320">               
                            <!-- 动态生成列 -->
                            <el-table-column v-for="column in tableSelectColumns" :key="column.prop" :prop="column.prop"
                                :label="column.label" :width="column.width">
                                <!-- 显示数据类型 -->
                                <el-table-column 
                                :prop="column.prop"
                                :label="column.type"  
                                :width="column.width"
                                ></el-table-column>
                            </el-table-column>
                        </el-table>
                        
                        <div v-else-if="loading" class="loading-text">数据加载中...</div>
                        <div v-else class="empty-text">暂无数据</div>
                        <!--分页工具条-->
                        <!-- <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="10"
                            layout="total, prev, pager, next, jumper" :total="cnt">
                        </el-pagination> -->
                    </div>
                    <div v-show="isTableShown">
                        <el-button 
                        type="primary" 
                        icon="el-icon-download" 
                        @click="downloadSelectData"
                        size = "small"
                        style="width: 80px; height: 35px;"
                    >
                        下载
                    </el-button>
                    </div>

                    <!-- <div class="line"></div> -->

                </div>
                <div class="display-result">
                    <div class="display-modal">
                        <!-- 表格 -->
                        <el-table v-if="tableResultData.length > 0 && tableResultColumns.length > 0"
                            :data="tableResultData" style="width: 500px; margin-top: 20px" max-height="300">
                            <!-- 动态生成列 -->
                            <el-table-column v-for="column in tableResultColumns" :key="column.prop" :prop="column.prop"
                                :label="column.label" :width="column.width">
                                <!-- 显示数据类型 -->
                                <el-table-column 
                                :prop="column.prop"
                                :label="column.type"  
                                :width="column.width"
                                ></el-table-column>
                            </el-table-column>       
                        </el-table>

                        <div v-else-if="loading" class="loading-text">数据加载中...</div>
                        <div v-else class="empty-text">暂无数据</div>
                    </div>
                    <div>
                        <el-button v-show="isImageShown"
                        type="primary" 
                        icon="el-icon-download" 
                        @click="downloadSelectData"
                        size = "small"
                        style="width: 80px; height: 35px;"
                    >
                        下载
                    </el-button>
                    </div>
                    <div ref="chartContainer1" style="width: 440px; height: 400px;"></div>
                    <div ref="chartContainer2" style="width: 440px; height: 400px;"></div>
                </div>
            </div>
        </div>

    </div>
</template>

<script>
// import { values } from 'core-js/core/array';
import Navbar from '../components/Navbar.vue';
import axios from 'axios';
import * as echarts from 'echarts';
import * as XLSX from 'xlsx';
export default {
    name: 'FlowF',
    components: {
        Navbar
    },
    data() {
        return {
            tableSelectData: [],
            tableResultData: [],
            tableSelectColumns: [],  // 列配置
            tableResultColumns: [],  // 列配置
            loading: false,
            imageUrl: '../assets/mode.jpg', // 图片地址
            isImageShown: false, // 控制图片和按钮显示的状态
            isTableShown: false, // 控制表格显示的状态
            props: { multiple: true },
            // 当前页码
            currentPage: 1,
            cnt: 800,
            selectedValue: [],//列表一被选中的数据
            listValue: [],
            processedData: {//// 处理后的表格数据
                materialType: '',
                tables: {}
            },
            options_data: [{
                value: '骨诱导相关',
                label: '骨诱导相关',
                children: [{
                    value: '材料组成成分',
                    label: '材料组成成分',
                    children: [
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "SampleName", label: "SampleName" },
                        { value: "MatConstitutionSerial", label: "MatConstitutionSerial" },
                        { value: "MatConstitutionConstName", label: "MatConstitutionConstName" },
                        { value: "MatConstitutionConstRepresentType", label: "MatConstitutionConstRepresentType" },
                        { value: "MatConstitutionConstDate", label: "MatConstitutionConstDate" },
                        { value: "MatConstitutionConstErrorRange", label: "MatConstitutionConstErrorRange" },
                        { value: "MatElementName", label: "MatElementName" },
                        { value: "MatElementRepresentType", label: "MatElementRepresentType" },
                        { value: "MatElementDate", label: "MatElementDate" },
                        { value: "MatElementErrorRan", label: "MatElementErrorRan" }
                    ]
                }, {
                    value: '基本物理性能',
                    label: '基本物理性能',
                    children: [
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "SampleName", label: "SampleName" },
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "Density", label: "Density" },
                        { value: "DensityUnit", label: "DensityUnit" },
                        { value: "MeltingPoint", label: "MeltingPoint" },
                        { value: "MeltingPointUnit", label: "MeltingPointUnit" },
                        { value: "PhaseTransitionTemperature", label: "PhaseTransitionTemperature" },
                        { value: "PhaseTransitionTemperatureUnit", label: "PhaseTransitionTemperatureUnit" },
                        { value: "Crystallinity", label: "Crystallinity" },
                        { value: "DegreeofPolymerization", label: "DegreeofPolymerization" },
                        { value: "pHValue", label: "pHValue" },
                        { value: "Color", label: "Color" },
                        { value: "CaPRatio", label: "CaPRatio" },
                        { value: "Granularity", label: "Granularity" },
                        { value: "GranularitySD", label: "GranularitySD" },
                        { value: "GranularityUnit", label: "GranularityUnit" }
                    ]
                }, {
                    value: '孔径相关性能',
                    label: '孔径相关性能',
                    children: [
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "SampleName", label: "SampleName" },
                        { value: "SpecificSurfaceAreaTestMethod", label: "SpecificSurfaceAreaTestMethod" },
                        { value: "SpecificSurfaceArea", label: "SpecificSurfaceArea" },
                        { value: "SpecificSurfaceAreaUnit", label: "SpecificSurfaceAreaUnit" },
                        { value: "AveragePoreDiameterTestMethod", label: "AveragePoreDiameterTestMethod" },
                        { value: "AveragePoreDiameter", label: "AveragePoreDiameter" },
                        { value: "AveragePoreDiameterSD", label: "AveragePoreDiameterSD" },
                        { value: "AveragePoreDiameterUnit", label: "AveragePoreDiameterUnit" },
                        { value: "PorosityTestMethod", label: "PorosityTestMethod" },
                        { value: "Porosity", label: "Porosity" },
                        { value: "PorositySD", label: "PorositySD" },
                        { value: "PorosityUnit", label: "PorosityUnit" },
                        { value: "TotalPoreArea", label: "TotalPoreArea" },
                        { value: "TotalPoreAreaSD", label: "TotalPoreAreaSD" },
                        { value: "TotalPoreAreaUnit", label: "TotalPoreAreaUnit" },
                        { value: "MicroporeDiameterMin", label: "MicroporeDiameterMin" },
                        { value: "MicroporeDiameterMax", label: "MicroporeDiameterMax" },
                        { value: "MicroporeDiameterunit", label: "MicroporeDiameterunit" },
                        { value: "MacroporeDiameterMin", label: "MacroporeDiameterMin" },
                        { value: "MacroporeDiameterMax", label: "MacroporeDiameterMax" },
                        { value: "MacroporeDiameterunit", label: "MacroporeDiameterunit" },
                        { value: "PoreSizeDistributionPhot", label: "PoreSizeDistributionPhot" }
                    ]
                }, {
                    value: '体内植入实验',
                    label: '体内植入实验',
                    children: [
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "SampleName", label: "SampleName" },
                        { value: "ImplantSampleShape", label: "ImplantSampleShape" },
                        { value: "ImplantSampleSizeDiameter", label: "ImplantSampleSizeDiameter" },
                        { value: "ImplantSampleSizeThickness", label: "ImplantSampleSizeThickness" },
                        { value: "ImplantSampleSizeLength", label: "ImplantSampleSizeLength" },
                        { value: "ImplantSampleSizeWidth", label: "ImplantSampleSizeWidth" },
                        { value: "ImplantSampleSizeHeight", label: "ImplantSampleSizeHeight" },
                        { value: "ImplantSampleSizeUnit", label: "ImplantSampleSizeUnit" },
                        { value: "ImplantSamplePreparation", label: "ImplantSamplePreparation" },
                        { value: "ImplantSampleNumber", label: "ImplantSampleNumber" },
                        { value: "ControlSample", label: "ControlSample" },
                        { value: "ControlSampleNumber", label: "ControlSampleNumber" },
                        { value: "AnimalSpecies", label: "AnimalSpecies" },
                        { value: "AnimalSpeciesSex", label: "AnimalSpeciesSex" },
                        { value: "AnimalSpeciesAge", label: "AnimalSpeciesAge" },
                        { value: "AnimalSpeciesWeight", label: "AnimalSpeciesWeight" },
                        { value: "ImplantSite", label: "ImplantSite" },
                        { value: "ImplantDuration", label: "ImplantDuration" },
                        { value: "ImplantDurationUnit", label: "ImplantDurationUnit" },
                        { value: "SurgicalCondition", label: "SurgicalCondition" },
                        { value: "TissueSampleProcessing", label: "TissueSampleProcessing" },
                        { value: "ImplantSiteTissueStructureChange", label: "ImplantSiteTissueStructureChange" },
                        { value: "ImplantSiteTissueReactionProperty", label: "ImplantSiteTissueReactionProperty" },
                        { value: "ImplantSiteTissueReactionLevel", label: "ImplantSiteTissueReactionLevel" },
                        { value: "ExistenceofImplant", label: "ExistenceofImplant" },
                        { value: "ShapeofImplant", label: "ShapeofImplant" },
                        { value: "PositionofImplant", label: "PositionofImplant" },
                        { value: "DegradationResidue", label: "DegradationResidue" },
                        { value: "FibrationLevel", label: "FibrationLevel" },
                        { value: "InflammationLevel", label: "InflammationLevel" },
                        { value: "InflammatoryCellType", label: "InflammatoryCellType" },
                        { value: "InflammatoryCellReaction", label: "InflammatoryCellReaction" },
                        { value: "NecrosisType", label: "NecrosisType" },
                        { value: "NecrosisLevel", label: "NecrosisLevel" },
                        { value: "OtherTissueChange", label: "OtherTissueChange" },
                        { value: "Osteogenesis", label: "Osteogenesis" },
                        { value: "OsteogenesisCondition", label: "OsteogenesisCondition" },
                        { value: "OsteogenesisAreaPercentage", label: "OsteogenesisAreaPercentage" },
                        { value: "OsteogenesisAreaPercentageSD", label: "OsteogenesisAreaPercentageSD" },
                        { value: "MaterialsResorption", label: "MaterialsResorption" },
                        { value: "MaterialsResorptionSD", label: "MaterialsResorptionSD" },
                        { value: "TissueSlice", label: "TissueSlice" },
                        { value: "NewboneElasticModulus", label: "NewboneElasticModulus" },
                        { value: "NewboneElasticModulusUnit", label: "NewboneElasticModulusUnit" },
                        { value: "NewboneTensileStrength", label: "NewboneTensileStrength" },
                        { value: "NewboneTensileStrengthUnit", label: "NewboneTensileStrengthUnit" },
                        { value: "NewboneCompressiveStrength", label: "NewboneCompressiveStrength" }
                    ]
                }, {
                    value: '文献数据来源',
                    label: '文献数据来源',
                    children: [
                        { value: "DocumentSerial", label: "DocumentSerial" },
                        { value: "DataSourceLiteratureType", label: "DataSourceLiteratureType" },
                        { value: "DataSourcePublicationName", label: "DataSourcePublicationName" },
                        { value: "DataSourceTitle", label: "DataSourceTitle" },
                        { value: "DataSourceAuthors", label: "DataSourceAuthors" },
                        { value: "DataSourceYear", label: "DataSourceYear" },
                        { value: "DataSourceVolume", label: "DataSourceVolume" },
                        { value: "DataSourceIssue", label: "DataSourceIssue" },
                        { value: "DataSourceStartPage", label: "DataSourceStartPage" },
                        { value: "DataSourceEndPage", label: "DataSourceEndPage" },
                        { value: "DataSourceArticleNo", label: "DataSourceArticleNo" },
                        { value: "DOI", label: "DOI" },
                        { value: "WOSNumber", label: "WOSNumber" },
                        { value: "ISSN", label: "ISSN" },
                        { value: "ISBN", label: "ISBN" },
                        { value: "DataSourceURL", label: "DataSourceURL" },
                        { value: "ProceedingsPaperMeeting", label: "ProceedingsPaperMeeting" },
                        { value: "ProceedingsPaperYear", label: "ProceedingsPaperYear" },
                        { value: "ProceedingsPaperLocation", label: "ProceedingsPaperLocation" },
                        { value: "DataSourceAbstract", label: "DataSourceAbstract" },
                        { value: "DataSourceFulltext", label: "DataSourceFulltext" }
                    ]
                }, {
                    value: '文献样品信息',
                    label: '文献样品信息',
                    children: [
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "SampleName", label: "SampleName" },
                        { value: "MaterialName", label: "MaterialName" },
                        { value: "SampleShape", label: "SampleShape" },
                        { value: "SampleSizeLength", label: "SampleSizeLength" },
                        { value: "SampleSizeWidth", label: "SampleSizeWidth" },
                        { value: "SampleSizeHeight", label: "SampleSizeHeight" },
                        { value: "SampleSizeDiameter", label: "SampleSizeDiameter" },
                        { value: "SampleSizeThickness", label: "SampleSizeThickness" },
                        { value: "SampleSizeUnit", label: "SampleSizeUnit" },
                        { value: "MatType", label: "MatType" },
                        { value: "MatSpecies", label: "MatSpecies" },
                        { value: "DocumentSerial", label: "DocumentSerial" }
                    ]
                }]
            }, {
                value: '类骨磷灰石',
                label: '类骨磷灰石',
                children: [{
                    value: '材料表面性能',
                    label: '材料表面性能',
                    children: [
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "SampleName", label: "SampleName" },
                        { value: "SurfaceTreatmentMethods", label: "SurfaceTreatmentMethods" },
                        { value: "ContactAngle", label: "ContactAngle" },
                        { value: "ContactAngleSD", label: "ContactAngleSD" },
                        { value: "ContactAngleUnit", label: "ContactAngleUnit" },
                        { value: "ContactAngleLiquidType", label: "ContactAngleLiquidType" },
                        { value: "SurfaceTension", label: "SurfaceTension" },
                        { value: "SurfaceTensionUnit", label: "SurfaceTensionUnit" },
                        { value: "ZetaPotential", label: "ZetaPotential" },
                        { value: "ZetaPotentialUnit", label: "ZetaPotentialUnit" },
                        { value: "SurfacePotentialSign", label: "SurfacePotentialSign" },
                        { value: "SurfacePotential", label: "SurfacePotential" },
                        { value: "SurfacePotentialUnit", label: "SurfacePotentialUnit" },
                        { value: "SurfaceEnergy", label: "SurfaceEnergy" },
                        { value: "SurfaceEnergyUnit", label: "SurfaceEnergyUnit" },
                        { value: "RoughnessCharacterization", label: "RoughnessCharacterization" },
                        { value: "RoughnessRa", label: "RoughnessRa" },
                        { value: "RoughnessRaSD", label: "RoughnessRaSD" },
                        { value: "RoughnessRaUnit", label: "RoughnessRaUnit" },
                        { value: "RoughnessRaRMS", label: "RoughnessRaRMS" },
                        { value: "RoughnessRaRMSSD", label: "RoughnessRaRMSSD" },
                        { value: "RoughnessRaRMSUnit", label: "RoughnessRaRMSUnit" },
                        { value: "MaximumRoughnessDepth", label: "MaximumRoughnessDepth" },
                        { value: "MaximumRoughnessDepthSD", label: "MaximumRoughnessDepthSD" },
                        { value: "MaximumRoughnessDepthUnit", label: "MaximumRoughnessDepthUnit" },
                        { value: "SurfaceMicrohardness", label: "SurfaceMicrohardness" },
                        { value: "SurfaceMicrohardnessSD", label: "SurfaceMicrohardnessSD" },
                        { value: "SurfaceMicrohardnessUnit", label: "SurfaceMicrohardnessUnit" },
                        { value: "CoatingAdhesionStrength", label: "CoatingAdhesionStrength" },
                        { value: "CoatingAdhesionStrengthSD", label: "CoatingAdhesionStrengthSD" },
                        { value: "CoatingAdhesionStrengthUnit", label: "CoatingAdhesionStrengthUnit" },
                        { value: "SurfaceMorphologyCharacterization", label: "SurfaceMorphologyCharacterization" },
                        { value: "SurfaceMorphology", label: "SurfaceMorphology" },
                        { value: "SurfaceMorphologyP", label: "SurfaceMorphologyP" }
                    ]
                }, {
                    value: '基本物理性能',
                    label: '基本物理性能',
                    children: [
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "SampleName", label: "SampleName" },
                        { value: "MatSpecies", label: "MatSpecies" },
                        { value: "Density", label: "Density" },
                        { value: "DensityUnit", label: "DensityUnit" },
                        { value: "MeltingPoint", label: "MeltingPoint" },
                        { value: "MeltingPointUnit", label: "MeltingPointUnit" },
                        { value: "PhaseTransitionTemperature", label: "PhaseTransitionTemperature" },
                        { value: "PhaseTransitionTemperatureUnit", label: "PhaseTransitionTemperatureUnit" },
                        { value: "Crystallinity", label: "Crystallinity" },
                        { value: "DegreeofPolymerization", label: "DegreeofPolymerization" },
                        { value: "pHValue", label: "pHValue" },
                        { value: "Color", label: "Color" },
                        { value: "CaPRatio", label: "CaPRatio" },
                        { value: "Granularity", label: "Granularity" },
                        { value: "GranularitySD", label: "GranularitySD" },
                        { value: "GranularityUnit", label: "GranularityUnit" }
                    ]
                }, {
                    value: '体外表面形成',
                    label: '体外表面形成',
                    children: [
                        { value: "SampleSerial", label: "SampleSerial" },
                        { value: "TypeofSBF", label: "TypeofSBF" },
                        { value: "ImmersionTime", label: "ImmersionTime" },
                        { value: "ImmersionTimeUnit", label: "ImmersionTimeUnit" },
                        { value: "AccumulationPoint", label: "AccumulationPoint" },
                        { value: "SurfaceConstitutionSerial", label: "SurfaceConstitutionSerial" },
                        { "value": "SurfaceElementCharacterization", "label": "SurfaceElementCharacterization" },
                        { "value": "SurfaceElementName", "label": "SurfaceElementName" },
                        { "value": "SurfaceElementRepresentType", "label": "SurfaceElementRepresentType" },
                        { "value": "SurfaceElementDate", "label": "SurfaceElementDate" },
                        { "value": "SurfaceElementErr", "label": "SurfaceElementErr" }
                    ]
                }, {
                    "value": "体外XRD",
                    "label": "体外XRD",
                    "children": [
                        { "value": "SampleSerial", "label": "SampleSerial" },
                        { "value": "TypeofSBF", "label": "TypeofSBF" },
                        { "value": "ImmersionTime", "label": "ImmersionTime" },
                        { "value": "ImmersionTimeUnit", "label": "ImmersionTimeUnit" }, // 去除"-"
                        { "value": "TypeofXRD", "label": "TypeofXRD" },
                        { "value": "EquipmentXRD", "label": "EquipmentXRD" },
                        { "value": "XRDCharacterization", "label": "XRDCharacterization" },
                        { "value": "DetectedPhase", "label": "DetectedPhase" },
                        { "value": "JCPDSNumber", "label": "JCPDSNumber" },
                        { "value": "ThetaDegree", "label": "ThetaDegree" },
                        { "value": "Millerindiceshkl", "label": "Millerindiceshkl" }, // 去除" "和"-"
                        { "value": "SpectraXRD", "label": "SpectraXRD" }
                    ]
                }, {
                    "value": "体外实验",
                    "label": "体外实验",
                    "children": [
                        { "value": "SampleSerial", "label": "SampleSerial" },
                        { "value": "SampleName", "label": "SampleName" },
                        { "value": "NucleationSite", "label": "NucleationSite" },
                        { "value": "TypeofSBF", "label": "TypeofSBF" },
                        { "value": "ComponentofSBF", "label": "ComponentofSBF" },
                        { "value": "SBFFlowSpeed", "label": "SBFFlowSpeed" },
                        { "value": "SBFFlowSpeedUnit", "label": "SBFFlowSpeedUnit" }, // 去除"-"
                        { "value": "ImmersionTime", "label": "ImmersionTime" },
                        { "value": "ImmersionTimeUnit", "label": "ImmersionTimeUnit" }, // 去除"-"
                        { "value": "FormationofBonelikeApatiteCharacterization", "label": "FormationofBonelikeApatiteCharacterization" }, // 去除"-"
                        { "value": "SEMResult", "label": "SEMResult" },
                        { "value": "SEMPhotos", "label": "SEMPhotos" }, // 去除"-"
                        { "value": "XRDPhase", "label": "XRDPhase" }, // 去除"-"
                        { "value": "XRDPhaseComposition", "label": "XRDPhaseComposition" }, // 去除"-"
                        { "value": "XRDPhotos", "label": "XRDPhotos" }, // 去除"-"
                        { "value": "FTIRResult", "label": "FTIRResult" },
                        { "value": "GrowthofApatite", "label": "GrowthofApatite" },
                        { "value": "GradeGrowthofApatite", "label": "GradeGrowthofApatite" } // 修正"Grage"为"Grade"并去除"-"
                    ]
                }, {
                    "value": "文献数据来源",
                    "label": "文献数据来源",
                    "children": [
                        { "value": "DocumentSerial", "label": "DocumentSerial" },
                        { "value": "DataSourceLiteratureType", "label": "DataSourceLiteratureType" },
                        { "value": "DataSourcePublicationName", "label": "DataSourcePublicationName" },
                        { "value": "DataSourceTitle", "label": "DataSourceTitle" },
                        { "value": "DataSourceAuthors", "label": "DataSourceAuthors" },
                        { "value": "DataSourceYear", "label": "DataSourceYear" },
                        { "value": "DataSourceVolume", "label": "DataSourceVolume" },
                        { "value": "DataSourceIssue", "label": "DataSourceIssue" },
                        { "value": "DataSourceStartPage", "label": "DataSourceStartPage" },
                        { "value": "DataSourceEndPage", "label": "DataSourceEndPage" },
                        { "value": "DataSourceArticleNo", "label": "DataSourceArticleNo" },
                        { "value": "DOI", "label": "DOI" },
                        { "value": "WOSNumber", "label": "WOSNumber" },
                        { "value": "ISSN", "label": "ISSN" },
                        { "value": "ISBN", "label": "ISBN" },
                        { "value": "DataSourceURL", "label": "DataSourceURL" },
                        { "value": "ProceedingsPaperMeeting", "label": "ProceedingsPaperMeeting" },
                        { "value": "ProceedingsPaperYear", "label": "ProceedingsPaperYear" },
                        { "value": "ProceedingsPaperLocation", "label": "ProceedingsPaperLocation" },
                        { "value": "DataSourceAbstract", "label": "DataSourceAbstract" },
                        { "value": "DataSourceFulltext", "label": "DataSourceFulltext" }
                    ]
                }, {
                    "value": "文献样品信息",
                    "label": "文献样品信息",
                    "children": [
                        { "value": "SampleSerial", "label": "SampleSerial" },
                        { "value": "SampleName", "label": "SampleName" },
                        { "value": "MaterialName", "label": "MaterialName" },
                        { "value": "SampleShape", "label": "SampleShape" },
                        { "value": "SampleSizeLength", "label": "SampleSizeLength" },
                        { "value": "SampleSizeWidth", "label": "SampleSizeWidth" },
                        { "value": "SampleSizeHeight", "label": "SampleSizeHeight" },
                        { "value": "SampleSizeDiameter", "label": "SampleSizeDiameter" },
                        { "value": "SampleSizeThickness", "label": "SampleSizeThickness" },
                        { "value": "SampleSizeUnit", "label": "SampleSizeUnit" }, // 去除"-"
                        { "value": "MatType", "label": "MatType" },
                        { "value": "MatSpecies", "label": "MatSpecies" },
                        { "value": "DocumentSerial", "label": "DocumentSerial" }
                    ]
                }]
            }, {
                "value": "工艺优化",
                "label": "工艺优化",
                "children": [
                    {
                        "value": "烧结工艺",
                        "label": "烧结工艺",
                        "children": [
                            { "value": "Numberexperiment", "label": "Numberexperiment" }, // 去除"_"
                            { "value": "curveid", "label": "curveid" }, // 去除"_"
                            { "value": "graphid", "label": "graphid" }, // 去除"_"
                            { "value": "Q", "label": "Q" },
                            { "value": "Diametershrinkagerate", "label": "Diametershrinkagerate" }, // 去除"_"和"-"
                            { "value": "Highshrinkagerate", "label": "Highshrinkagerate" }, // 去除"_"和"-"
                            { "value": "porosity", "label": "porosity" },
                            { "value": "id", "label": "id" },
                            { "value": "source", "label": "source" },
                            { "value": "target", "label": "target" },
                            { "value": "weight", "label": "weight" },
                            { "value": "edgeid", "label": "edgeid" }, // 去除"_"
                            { "value": "idx", "label": "idx" },
                            { "value": "id0", "label": "id0" }, // 去除"_[0]"中的特殊符号
                            { "value": "temp", "label": "temp" },
                            { "value": "hold", "label": "hold" }
                        ]
                    }, {
                        "value": "几何结构",
                        "label": "几何结构",
                        "children": [
                            { "value": "Numberexperiment", "label": "Numberexperiment" }, // 去除"_"
                            { "value": "curveid", "label": "curveid" }, // 去除"_"
                            { "value": "graphid", "label": "graphid" }, // 去除"_"
                            { "value": "Q", "label": "Q" },
                            { "value": "Diametershrinkagerate", "label": "Diametershrinkagerate" }, // 去除"_"和"-"
                            { "value": "Highshrinkagerate", "label": "Highshrinkagerate" }, // 去除"_"和"-"
                            { "value": "porosity", "label": "porosity" },
                            { "value": "id", "label": "id" },
                            { "value": "source", "label": "source" },
                            { "value": "target", "label": "target" },
                            { "value": "weight", "label": "weight" },
                            { "value": "edgeid", "label": "edgeid" }, // 去除"_"
                            { "value": "idx", "label": "idx" },
                            { "value": "id0", "label": "id0" }, // 去除"_[0]"中的特殊符号
                            { "value": "x", "label": "x" },
                            { "value": "y", "label": "y" },
                            { "value": "z", "label": "z" },
                            { "value": "feature", "label": "feature" },
                            { "value": "active", "label": "active" }
                        ]
                    }, {
                        "value": "力学性能评价",
                        "label": "力学性能评价",
                        "children": [
                            { "value": "Id", "label": "Id" },
                            { "value": "Numberexperiment", "label": "Numberexperiment" }, // 去除"_"
                            { "value": "CreatedAt", "label": "CreatedAt" },
                            { "value": "UpdatedAt", "label": "UpdatedAt" },
                            { "value": "curveid", "label": "curveid" }, // 去除"_"
                            { "value": "graphid", "label": "graphid" }, // 去除"_"
                            { "value": "Q", "label": "Q" },
                            { "value": "Diametershrinkagerate", "label": "Diametershrinkagerate" }, // 去除"_"和"-"
                            { "value": "Highshrinkagerate", "label": "Highshrinkagerate" }, // 去除"_"和"-"
                            { "value": "porosity", "label": "porosity" }
                        ]
                    }]
            }, {
                "value": "高通量实验",
                "label": "高通量实验",
                "children": [
                    {
                        "value": "体内",
                        "label": "体内",
                        "children": [
                            { "value": "Poreshape", "label": "Poreshape" }, // 去除"_"
                            { "value": "ModelPorosity", "label": "ModelPorosity" }, // 去除"_"
                            { "value": "SpecificSurfaceArea", "label": "SpecificSurfaceArea" }, // 去除"_"
                            { "value": "Permeability", "label": "Permeability" },
                            { "value": "BV/TV", "label": "BV/TV" }, // 保留"/"
                            { "value": "EffectivePorosity", "label": "EffectivePorosity" } // 去除"_"
                        ]
                    }, {
                        "value": "体外",
                        "label": "体外",
                        "children": [
                            { "value": "Poreshape", "label": "Poreshape" }, // 去除空格
                            { "value": "ModelPorosity", "label": "ModelPorosity" }, // 去除空格
                            { "value": "SpecificSurfaceArea", "label": "SpecificSurfaceArea" }, // 去除空格
                            { "value": "Permeability", "label": "Permeability" },
                            { "value": "day", "label": "day" },
                            { "value": "ALP", "label": "ALP" },
                            { "value": "COL1", "label": "COL1" }, // 去除"-"
                            { "value": "OCN", "label": "OCN" },
                            { "value": "OPN", "label": "OPN" },
                            { "value": "RUNX2", "label": "RUNX2" } // 去除"-"
                        ]
                    }]
            }],
            matrics: [],
            options_model: [{
                value: 'linear_regression',
                label: '线性回归'
            }, {
                value: 'xgboost_classification',
                label: 'Xgboost分类'
            }, {
                value: 'xgboost_regression',
                label: 'Xgboost回归'
            }],
            options_insert: [{
                value: 'KNN',
                label: 'KNN'
            }, {
                value: 'MICE',
                label: 'MICE'
            }, {
                value: 'MEAN',
                label: 'MEAN'
            }],
            value_model: '',
            value_insert: ''
        };
    },
    mounted() {

    },
    methods: {
        // 处理选中的数据
        processSelectedData(selectedValue) {
            // 重置处理后的数据
            this.processedData = {
                materialType: '',
                tables: {}
            };

            if (!selectedValue || selectedValue.length === 0) return;

            // 提取材料类型（第一级）
            const materialTypes = new Set();
            selectedValue.forEach(path => {
                if (path && path.length > 0) {
                    materialTypes.add(path[0]);
                }
            });

            // 目前只处理第一个材料类型（根据需求调整）
            if (materialTypes.size > 0) {
                this.processedData.materialType = Array.from(materialTypes)[0];

                // 处理表格和字段
                selectedValue.forEach(path => {
                    if (path && path.length === 3) { // 确保是三级路径
                        const tableType = path[1];
                        const field = path[2];

                        // 初始化表格类型的字段数组
                        if (!this.processedData.tables[tableType]) {
                            this.processedData.tables[tableType] = [];
                        }

                        // 添加字段到对应表格
                        if (!this.processedData.tables[tableType].includes(field)) {
                            this.processedData.tables[tableType].push(field);
                        }
                    }
                });
            }
            console.log(this.processedData);
        },
        fetchTableSelectData() {
            this.loading = true;
            this.isTableShown = true;
            this.tableSelectData = [
            ];
            this.tableSelectColumns = [
            ];

            try {
                this.$request.post(
                    'http://192.168.26.251:8083/basemodule/search/dynamic',
                    this.processedData
                ).then(res => {
                    console.log(res.data.data);
                    if (res.data.msg === 'success') {
                        // 解构赋值获取列配置和表格数据
                        // const { columns, rows } = res.data.data;
                        // this.tableColumns = columns;
                        // this.tableData = rows;
                        console.log(res.data.data);
                        const data = res.data.data;

                        //提取所有唯一的字段名作为列（columns）
                        const columns = Object.keys(data[0]).map(key => ({
                            prop: key, // 对应数据中的字段名
                            label: key // 列名
                        }));

                        // 赋值给组件的表格数据
                        this.tableSelectData = data;
                        this.tableSelectColumns = columns;
                    } else {
                        this.$message.error('请求失败，请重试');
                    }
                })
            } catch (error) {
                console.error('获取数据失败:', error);
                this.$message.error('网络错误，请检查后端连接');
            } finally {
                this.loading = false;
            }
            // const res = this.$request.post(
            //     'http://192.168.27.105:8083/basemodule/search/dynamic',
            //     this.processedData
            // );
            //     console.log(res.data);
            //     if (res.data.msg === "success") {
            //     // 解构赋值获取列配置和表格数据
            //     const { columns, rows } = res.data.data;
            //     this.tableColumns = columns;
            //     this.tableData = rows;
            //     } else {
            //     this.$message.error('请求失败，请重试');
            //     }
            // } catch (error) {
            //     console.error('获取数据失败:', error);
            //     this.$message.error('网络错误，请检查后端连接');
            // } finally {
            //     this.loading = false;
            // }

        },
        fetchTableResultData() {
            var _this = this;
            this.isImageShown = true;
            var tableSelectColumns = Object.keys(this.tableSelectData[0])
            console.log(tableSelectColumns);
            console.log(_this.value_model);

            // 将表连接的数据传给机器学习模型进行处理, 得到结果数据——tableResultData
            axios({
                method: "post",
                url: "http://192.168.26.251:8081/ml/Linear_regress/train_and_predict",
                data: {
                    task: _this.value_model,
                    targetColumn: tableSelectColumns[0],
                    tableData: _this.tableSelectData,
                }
            }).then(function (resp) {
                console.log(resp.data);
                var matrics = Object.values(resp.data['matrics']);
                console.log(matrics);
                _this.initChart1(resp.data);
                _this.initChart2(matrics);
                //提取所有唯一的字段名作为列（columns）
                const columns = Object.keys(resp.data.predictions[0]).map(key => ({
                    prop: key, // 对应数据中的字段名
                    label: key // 列名
                }));
                // 赋值给组件的表格数据
                _this.tableResultData = resp.data.predictions;
                _this.tableResultColumns = columns;
                console.log(_this.tableResultData);
            }).catch((error) => {
                console.error('请求失败:', error)
            })
            // this.loading = true;
            // this.isImageShown = true;
            // this.tableResultData = [
            // {
            //     "id": 1,
            //     "username": "admin",
            //     "email": "admin@example.com",
            //     "status": "active", // 状态值（与formatter对应）
            //     "createTime": "2023-10-01T12:00:00"
            // },
            // {
            //     "id": 2,
            //     "username": "user001",
            //     "email": "user001@example.com",
            //     "status": "inactive",
            //     "createTime": "2023-10-02T14:30:00"
            // },
            // {
            //     "id": 3,
            //     "username": "guest",
            //     "email": "guest@example.com",
            //     "status": "pending",
            //     "createTime": "2023-10-03T09:15:00"
            // }
            // ];
            // this.tableResultColumns = [
            // {
            //     "prop": "id",
            //     "label": "ID",
            //     "width": "80",
            //     "sortable": true // 支持排序（可选）
            // },
            // {
            //     "prop": "username",
            //     "label": "用户名",
            //     "width": "120",
            //     "sortable": true
            // },
            // {
            //     "prop": "email",
            //     "label": "邮箱",
            //     "width": "200"
            // },
            // {
            //     "prop": "status",
            //     "label": "状态",
            //     "width": "100",
            //     "formatter": "statusFormatter" // 自定义渲染方法（可选）
            // },
            // {
            //     "prop": "createTime",
            //     "label": "创建时间",
            //     "width": "180",
            //     "sortable": true
            // }
            // ];

            // try {
            //     const response = this.$axios.get(
            //     // 'http://192.168.27.13:18080/basemodule/user/listWithColumns'
            //     'https://mock-api.doubao.com/table-data'
            //     );

            //     if (response.status === 200) {
            //     // 解构赋值获取列配置和表格数据
            //     const { columns, rows } = response.data.data;
            //     this.tableColumns = columns;
            //     this.tableData = rows;
            //     } else {
            //     this.$message.error('请求失败，请重试');
            //     }
            // } catch (error) {
            //     console.error('获取数据失败:', error);
            //     this.$message.error('网络错误，请检查后端连接');
            // } finally {
            //     this.loading = false;
            // }
        },
        // 下载表格数据
        downloadSelectData() {
            // 这里假设allTableData是包含所有查询结果的数据
            // 如果需要从服务器获取完整数据，可以在这里添加请求逻辑
            if (this.cnt === 0) {
                console.log(this.cnt);
                this.$message.warning('没有可下载的数据');
                return;
            }
            try {
                // 转换数据格式
                const exportData = this.tableSelectData.map(item => {
                    const formattedItem = {};
                    // 根据列名映射数据，确保导出的表头与表格一致
                    console.log(this.tableSelectData);
                    this.tableSelectColumns.forEach(col => {
                        formattedItem[col.label] = item[col.prop];
                    });
                    return formattedItem;
                });
                
                // 创建工作簿和工作表
                const worksheet = XLSX.utils.json_to_sheet(exportData);
                const workbook = XLSX.utils.book_new();
                XLSX.utils.book_append_sheet(workbook, worksheet, '查询数据');
                
                // 生成包含当前日期的文件名
                const date = new Date();
                const fileName = `查询数据_${date.getFullYear()}${(date.getMonth()+1).toString().padStart(2, '0')}${date.getDate().toString().padStart(2, '0')}.xlsx`;
                
                // 下载文件
                XLSX.writeFile(workbook, fileName);
                this.$message.success('数据下载成功');
            } catch (error) {
                console.error('下载失败:', error);
                this.$message.error('数据下载失败，请稍后重试');
            }
        },
        initChart2(val) {
            // 获取图表容器的引用
            const chartDom = this.$refs.chartContainer2;
            // 初始化 ECharts 实例
            const myChart = echarts.init(chartDom);
            // 配置图表选项
            const option = {
                legend: {
                    data: ['Matrics']
                },
                radar: {
                    // shape: 'circle',
                    indicator: [
                        { name: 'MSE', max: 10 },
                        { name: 'MAE', max: 5 },
                        { name: 'R2', max: 1 },
                        { name: 'Explained Var', max: 1 },
                        { name: 'RSS', max: 2000 },
                        { name: 'TSS', max: 2000 },
                        { name: 'SSR', max: 1000 },
                        { name: 'SSE', max: 2000 },         
                    ]
                },
                series: [
                    {
                        name: 'Budget vs spending',
                        type: 'radar',
                        data: [
                            {
                                value: val,
                                name: 'Matrics'
                            }
                        ]
                    }
                ]
            };
            // 使用刚指定的配置项和数据显示图表
            if (option && typeof option === 'object') {
                myChart.setOption(option);
            }
            // 监听窗口大小变化，重新调整图表大小
            window.addEventListener('resize', () => {
                myChart.resize();
            });
        },
        handleDropdownAction(action) {
            console.log('下拉菜单点击:', action);
            // 根据action执行不同操作
            switch (action) {
                case 'profile':
                    // 跳转个人中心
                    this.$router.push('/person');
                    break;
                case 'logout':
                    // 执行退出登录
                    this.$router.push('/login');
                    break;
            }
        },
        //分页
        handleCurrentChange(val) {
            console.log(`当前页: ${val}`);
            this.currentPage = val;
            // 根据当前页重新确定新的 tabelData
            this.usedTableData = this.allData.slice(10 * (val - 1), 10 * val);
        },
        initChart1(val) {
            // 获取图表容器的引用
            const chartDom = this.$refs.chartContainer1;
            // 初始化 ECharts 实例
            const myChart = echarts.init(chartDom);
            // 转换为 ECharts 需要的格式
            const scatterData = val.predictions.map(item => [
            item.true_target,  // x 轴：真实值
            item.predicted    // y 轴：预测值
            ]);
            // 配置图表选项
            const option = {
                xAxis: {    type: 'value',
                    name: 'True',
                    min: 2,         // 固定最小值
                    max: 12,        // 固定最大值
                    interval: 2,    // 刻度间隔为 2（显示 2、4、6、8、10、12）
                    axisTick: {
                    alignWithLabel: true // 刻度线与标签对齐
                    }
                },
                yAxis: {
                    type: 'value',
                    name: 'Predicted',
                    min: 2,
                    max: 12,
                    interval: 2,
                    axisLine: {
                    lineStyle: { color: '#ddd' } // 轴线样式
                    }
                },
                series: [
                    {
                        symbolSize: 15,
                        data:  scatterData,
                        type: 'scatter'
                    }
                ]
            };
            // 使用刚指定的配置项和数据显示图表
            if (option && typeof option === 'object') {
                myChart.setOption(option);
            }
            // 监听窗口大小变化，重新调整图表大小
            window.addEventListener('resize', () => {
                myChart.resize();
            });
        },
    }
};
</script>

<style scoped>
/* content-wrapper样式 - 占据除Navbar外的所有区域 */
.content-wrapper {
    flex: 1;
    /* 占据剩余的所有空间 */
    display: flex;
    /* 创建一个flex容器 */
    /* height: 100%; */
    height: 90vh;
    /* 占据剩余的整个高度 */
}

/* select-wrapper样式 - 左侧部分 */
.select-wrapper {
    width: 20%;
    /* 占据父容器的25%宽度 */
    flex-shrink: 0;
    /* 防止在缩小窗口时被压缩 */
    display: flex;
    flex-direction: column;
    /* 子元素垂直排列 */
    border: 3px solid #ddd;
    border-radius: 10px;
    /* 设置圆角 */
    /* 添加边框以便区分 */
}

/* display-wrapper样式 - 右侧部分 */
.display-wrapper {
    flex: 1;
    /* 占据父容器的剩余空间 */
    display: flex;
    flex-direction: column;
    /* 子元素垂直排列 */
}

/* select-wrapper的子元素样式 */
.select-data {
    flex: 1;
    /* 占据相等的垂直空间 */
    padding: 10px;
    margin: 5px;
    height: 45%;
}

.select-data * {
    margin-bottom: 50px;
    /* 每个子元素底部间距 */
}

.select-model {
    flex: 1;
    /* 占据相等的垂直空间 */
    padding: 10px;
    margin: 5px;
    height: 45%;
}

/* display-wrapper的子元素样式 */
.display-select,
.display-result {
    display: flex;
    flex: 1;
    /* 占据相等的垂直空间 */
    border: 3px solid #ddd;
    border-radius: 10px;
    /* 设置圆角 */
    /* 添加边框以便区分 */
    padding: 15px;
    margin: 5px;
    overflow: auto;
    /* 如果内容过多，添加滚动条 */
}

.separator {
    width: 90%;
    height: 2px;
    background-color: #d5d4d4;
    margin: 0 5%;
}

.select-button {
    padding-left: 54%;
    padding-bottom: 8%;
}

.table-container {
    position: relative;
    /* 关键：为绝对定位的子元素提供参考 */
    max-width: 700px;
    /* 最大宽度为800像素，当内容或父容器变化使宽度超过此值时，保持800px */
    min-width: 300px;
    flex: 1;
}

.image-button-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    margin-top: 45px;
    gap: 5px;
    max-width: 500px;
    /* 最大宽度为800像素，当内容或父容器变化使宽度超过此值时，保持800px */
    min-width: 100px;
    flex: 0 0 1300px;
    /* 右侧固定宽度300px（不随容器缩放） */
}


.main-image {
    max-width: 180px;
    max-height: 280px;
    /* display: block;  */
}


.button-container {
    width: 100%;
    text-align: center;
    margin-top: 40px;
}

.el-button {
    width: 120px;
}

.line {
    width: 100px;
    height: 2px;
    margin-top: 150px;
    background-color: #000;
}

/* .custom-cascader .el-input__inner {
    display: block;
  max-height: calc(1.5em * 2); /* 2 行高度，1.5em 为行高 */
/* overflow: hidden;
  white-space: normal;
} */
</style>
<template>
    <div>
        <!-- 固定在顶部的导航栏 -->
        <Navbar @dropdown-action="handleDropdownAction" />

        <!-- 一个固定高度的面板——搜索栏 -->
        <div class="search-container">
            <div class="search-bar">
                <el-cascader :options="options" @change="handleChange" size="large" :props="{ checkStrictly: true }"
                    clearable></el-cascader>

                <el-input v-model="search_input" placeholder="输入具体检索内容..." size="large"></el-input>
                <el-button type="primary" icon="el-icon-search" @click="search" size="large"
                    style="width: 90px;">搜索</el-button>
            </div>
        </div>

        <div class="search-display">
            <div class="konghang"></div>
            <!-- 选择在哪些列中进行查询 -->
            <div class="filter-box" v-if="showSearchDisplay">
                <el-checkbox :indeterminate="isIndeterminate" v-model="checkAll"
                    @change="handleCheckAllChange">全选</el-checkbox>
                <div style="margin: 10px 0;"></div>
                <el-checkbox-group v-model="checkedCols" @change="handleCheckedColsChange"
                    style="display: flex; flex-wrap: wrap; justify-content: flex-start;">
                    <el-checkbox v-for="col in selected_cols" :label="col" :key="col" style="margin-right: 20px;">{{ col
                        }}</el-checkbox>
                </el-checkbox-group>
                <div style="margin: 10px 0;"></div>
                <div class="button-container">
                    <el-button type="primary" @click="display_cols" round>确定</el-button>
                </div>
            </div>
            <div class="search-data-box" v-if="showSearchDisplay">
                <!-- 展示搜索的数据 -->
                <el-table :data="usedTableData" border style="width: 100%; " size="large">

                    <el-table-column v-for="col in cols" :prop="col" :label="col" :key="col" width="200px">
                    </el-table-column>

                </el-table>
                <!-- 分页和下载按钮 -->
                <div class="pagination-container"><!--分页工具条-->
                    <el-pagination @current-change="handleCurrentChange" :current-page="currentPage" :page-size="10"
                        layout="total, prev, pager, next, jumper" :total="cnt">
                    </el-pagination>
                    <el-button 
                        type="primary" 
                        icon="el-icon-download" 
                        @click="downloadAllData"
                        size = "large"
                        style="width: 80px; height: 35px;"
                    >
                        下载
                    </el-button>
                </div>
            </div>
            <div class="picture-block" v-if="showPictureDisplay">
                <el-image :src="src">
                    <div slot="placeholder" class="image-slot">
                        加载中<span class="dot">...</span>
                    </div>
                </el-image>
            </div>
        </div>
    </div>
</template>


<script>
import Navbar from '../components/Navbar.vue';
import axios from 'axios';
// 在组件的 script 部分顶部导入
import * as XLSX from 'xlsx';
export default {
    name: "SearchS",
    components: {
        Navbar
    },
    data() {
        return {
            userName: '用户名',
            circleUrl: "https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png",
            // 搜索的关键字
            search_input: '',
            // 是否显示表格搜索内容
            showSearchDisplay: false,
            // 是否展示图片搜索内容
            showPictureDisplay: false,
            // 搜索的选项
            options: [{
                value: '骨诱导',
                label: '骨诱导相关',
                children: [{
                    value: '材料组成成分',
                    label: '材料组成成分',
                    children: [
                        { value: "sampleserial", label: "sampleserial" },
                        { value: "samplename", label: "samplename" },
                        { value: "matconstitutionserial", label: "matconstitutionserial" },
                        { value: "matconstitutionconstname", label: "matconstitutionconstname" },
                        { value: "matconstitutionconstrepresenttype", label: "matconstitutionconstrepresenttype" },
                        { value: "matconstitutionconstdate", label: "matconstitutionconstdate" },
                        { value: "matconstitutionconsterrorrange", label: "matconstitutionconsterrorrange" },
                        { value: "matelementname", label: "matelementname" },
                        { value: "matelementrepresenttype", label: "matelementrepresenttype" },
                        { value: "matelementdate", label: "matelementdate" },
                        { value: "matelementerrorrange", label: "matelementerrorrange" }
                    ]
                }, {
                    value: '基本物理性能',
                    label: '基本物理性能',
                    children: [
                        { value: "sampleserial", label: "sampleserial" },
                        { value: "samplename", label: "samplename" },
                        { value: "matspecies", label: "matspecies" },
                        { value: "density", label: "density" },
                        { value: "densityUnit", label: "densityUnit" },
                        { value: "meltingpoint", label: "meltingpoint" },
                        { value: "meltingpointUnit", label: "meltingpointUnit" },
                        { value: "phasetransitiontemperature", label: "phasetransitiontemperature" },
                        { value: "phasetransitiontemperatureUnit", label: "phasetransitiontemperatureUnit" },
                        { value: "crystallinity", label: "crystallinity" },
                        { value: "degreeofpolymerization", label: "degreeofpolymerization" },
                        { value: "phvalue", label: "phvalue" },
                        { value: "color", label: "color" },
                        { value: "capRatio", label: "capRatio" },
                        { value: "granularity", label: "granularity" },
                        { value: "granularitySd", label: "granularitySd" },
                        { value: "granularityUnit", label: "granularityUnit" }
                    ]
                }, {
                    value: '孔径相关性能',
                    label: '孔径相关性能',
                    children: [
                        { value: "sampleserial", label: "sampleserial" },
                        { value: "samplename", label: "samplename" },
                        { value: "specificsurfaceareaTestmethod", label: "specificsurfaceareaTestmethod" },
                        { value: "specificsurfacearea", label: "specificsurfacearea" },
                        { value: "specificsurfaceareaUnit", label: "specificsurfaceareaUnit" },
                        { value: "averageporediameterTestmethod", label: "averageporediameterTestmethod" },
                        { value: "averageporediameter", label: "averageporediameter" },
                        { value: "averageporediameterSd", label: "averageporediameterSd" },
                        { value: "averageporediameterUnit", label: "averageporediameterUnit" },
                        { value: "porosityTestmethod", label: "porosityTestmethod" },
                        { value: "porosity", label: "porosity" },
                        { value: "porositySd", label: "porositySd" },
                        { value: "porosityUnit", label: "porosityUnit" },
                        { value: "totalporearea", label: "totalporearea" },
                        { value: "totalporeareaSd", label: "totalporeareaSd" },
                        { value: "totalporeareaUnit", label: "totalporeareaUnit" },
                        { value: "microporediameterMin", label: "microporediameterMin" },
                        { value: "microporediameterMax", label: "microporediameterMax" },
                        { value: "microporediameterUnit", label: "microporediameterUnit" },
                        { value: "macroporediameterMin", label: "macroporediameterMin" },
                        { value: "macroporediameterMax", label: "macroporediameterMax" },
                        { value: "macroporediameterUnit", label: "macroporediameterUnit" },
                        { value: "poresizedistributionphotos", label: "poresizedistributionphotos" }
                    ]
                }, {
                    value: '体内植入实验',
                    label: '体内植入实验',
                    children: [
                        { value: "sampleserial", label: "sampleserial" },
                        { value: "samplename", label: "samplename" },
                        { value: "implantsampleshape", label: "implantsampleshape" },
                        { value: "implantsamplesizediameter", label: "implantsamplesizediameter" },
                        { value: "implantsamplesizethickness", label: "implantsamplesizethickness" },
                        { value: "implantsamplesizelength", label: "implantsamplesizelength" },
                        { value: "implantsamplesizewidth", label: "implantsamplesizewidth" },
                        { value: "implantsamplesizeheight", label: "implantsamplesizeheight" },
                        { value: "implantsamplesizeUnit", label: "implantsamplesizeUnit" },
                        { value: "implantsamplepreparation", label: "implantsamplepreparation" },
                        { value: "implantsamplenumber", label: "implantsamplenumber" },
                        { value: "controlsample", label: "controlsample" },
                        { value: "controlsamplenumber", label: "controlsamplenumber" },
                        { value: "animalspecies", label: "animalspecies" },
                        { value: "animalspeciessex", label: "animalspeciessex" },
                        { value: "animalspeciesage", label: "animalspeciesage" },
                        { value: "animalspeciesweight", label: "animalspeciesweight" },
                        { value: "implantsite", label: "implantsite" },
                        { value: "implantduration", label: "implantduration" },
                        { value: "implantdurationUnit", label: "implantdurationUnit" },
                        { value: "surgicalcondition", label: "surgicalcondition" },
                        { value: "tissuesampleprocessing", label: "tissuesampleprocessing" },
                        { value: "implantsitetissuestructurechange", label: "implantsitetissuestructurechange" },
                        { value: "implantsitetissuereactionproperty", label: "implantsitetissuereactionproperty" },
                        { value: "implantsitetissuereactionlevel", label: "implantsitetissuereactionlevel" },
                        { value: "existenceofimplant", label: "existenceofimplant" },
                        { value: "shapeofimplant", label: "shapeofimplant" },
                        { value: "positionofimplant", label: "positionofimplant" },
                        { value: "degradationresidue", label: "degradationresidue" },
                        { value: "fibrationlevel", label: "fibrationlevel" },
                        { value: "inflammationlevel", label: "inflammationlevel" },
                        { value: "inflammatorycelltype", label: "inflammatorycelltype" },
                        { value: "inflammatorycellreaction", label: "inflammatorycellreaction" },
                        { value: "necrosistype", label: "necrosistype" },
                        { value: "necrosislevel", label: "necrosislevel" },
                        { value: "othertissuechange", label: "othertissuechange" },
                        { value: "osteogenesis", label: "osteogenesis" },
                        { value: "osteogenesiscondition", label: "osteogenesiscondition" },
                        { value: "osteogenesisareapercentage", label: "osteogenesisareapercentage" },
                        { value: "osteogenesisareapercentageSd", label: "osteogenesisareapercentageSd" },
                        { value: "materialsresorption", label: "materialsresorption" },
                        { value: "materialsresorptionSd", label: "materialsresorptionSd" },
                        { value: "tissueslice", label: "tissueslice" },
                        { value: "newboneelasticmodulus", label: "newboneelasticmodulus" },
                        { value: "newboneelasticmodulusUnit", label: "newboneelasticmodulusUnit" },
                        { value: "newbonetensilestrength", label: "newbonetensilestrength" },
                        { value: "newbonetensilestrengthUnit", label: "newbonetensilestrengthUnit" },
                        { value: "newbonecompressivestrength", label: "newbonecompressivestrength" },
                        { value: "newbonecompressivestrengthUnit", label: "newbonecompressivestrengthUnit" }
                    ]
                }, {
                    value: '文献数据来源',
                    label: '文献数据来源',
                    children: [
                        { value: "documentserial", label: "documentserial" },
                        { value: "datasourceliteraturetype", label: "datasourceliteraturetype" },
                        { value: "datasourcepublicationname", label: "datasourcepublicationname" },
                        { value: "datasourcetitle", label: "datasourcetitle" },
                        { value: "datasourceauthors", label: "datasourceauthors" },
                        { value: "datasourceyear", label: "datasourceyear" },
                        { value: "datasourcevolume", label: "datasourcevolume" },
                        { value: "datasourceissue", label: "datasourceissue" },
                        { value: "datasourcestartpage", label: "datasourcestartpage" },
                        { value: "datasourceendpage", label: "datasourceendpage" },
                        { value: "datasourcearticleno", label: "datasourcearticleno" },
                        { value: "doi", label: "doi" },
                        { value: "wosnumber", label: "wosnumber" },
                        { value: "issn", label: "issn" },
                        { value: "isbn", label: "isbn" },
                        { value: "datasourceurl", label: "datasourceurl" },
                        { value: "proceedingspapermeeting", label: "proceedingspapermeeting" },
                        { value: "proceedingspaperyear", label: "proceedingspaperyear" },
                        { value: "proceedingspaperlocation", label: "proceedingspaperlocation" },
                        { value: "datasourceabstract", label: "datasourceabstract" },
                        { value: "datasourcefulltext", label: "datasourcefulltext" }
                    ]
                }, {
                    value: '文献样品信息',
                    label: '文献样品信息',
                    children: [
                        { value: "sampleserial", label: "sampleserial" },
                        { value: "samplename", label: "samplename" },
                        { value: "materialname", label: "materialname" },
                        { value: "sampleshape", label: "sampleshape" },
                        { value: "samplesizelength", label: "samplesizelength" },
                        { value: "samplesizewidth", label: "samplesizewidth" },
                        { value: "samplesizeheight", label: "samplesizeheight" },
                        { value: "samplesizediameter", label: "samplesizediameter" },
                        { value: "samplesizethickness", label: "samplesizethickness" },
                        { value: "samplesizeUnit", label: "samplesizeUnit" },
                        { value: "mattype", label: "mattype" },
                        { value: "matspecies", label: "matspecies" },
                        { value: "documentserial", label: "documentserial" }
                    ]
                }]
            }, {
                value: '类骨磷灰石',
                label: '类骨磷灰石',
                children: [{
                    value: '材料表面性能',
                    label: '材料表面性能',
                    children: [
                        { "value": "sampleserial", "label": "sampleserial" },
                        { "value": "samplename", "label": "samplename" },
                        { "value": "surfacetreatmentmethods", "label": "surfacetreatmentmethods" },
                        { "value": "contactangle", "label": "contactangle" },
                        { "value": "contactangleSd", "label": "contactangleSd" },
                        { "value": "contactangleUnit", "label": "contactangleUnit" },
                        { "value": "contactangleLiquidtype", "label": "contactangleLiquidtype" },
                        { "value": "surfacetension", "label": "surfacetension" },
                        { "value": "surfacetensionunit", "label": "surfacetensionunit" },
                        { "value": "zetapotential", "label": "zetapotential" },
                        { "value": "zetapotentialUnit", "label": "zetapotentialUnit" },
                        { "value": "surfacepotentialsign", "label": "surfacepotentialsign" },
                        { "value": "surfacepotential", "label": "surfacepotential" },
                        { "value": "surfacepotentialUnit", "label": "surfacepotentialUnit" },
                        { "value": "surfaceenergy", "label": "surfaceenergy" },
                        { "value": "surfaceenergyUnit", "label": "surfaceenergyUnit" },
                        { "value": "roughnesscharacterization", "label": "roughnesscharacterization" },
                        { "value": "roughnessra", "label": "roughnessra" },
                        { "value": "roughnessraSd", "label": "roughnessraSd" },
                        { "value": "roughnessraUnit", "label": "roughnessraUnit" },
                        { "value": "roughnessrarms", "label": "roughnessrarms" },
                        { "value": "roughnessrarmsSd", "label": "roughnessrarmsSd" },
                        { "value": "roughnessrarmsUnit", "label": "roughnessrarmsUnit" },
                        { "value": "maximumroughnessdepth", "label": "maximumroughnessdepth" },
                        { "value": "maximumroughnessdepthSd", "label": "maximumroughnessdepthSd" },
                        { "value": "maximumroughnessdepthUnit", "label": "maximumroughnessdepthUnit" },
                        { "value": "surfacemicrohardness", "label": "surfacemicrohardness" },
                        { "value": "surfacemicrohardnessSd", "label": "surfacemicrohardnessSd" },
                        { "value": "surfacemicrohardnessUnit", "label": "surfacemicrohardnessUnit" },
                        { "value": "coatingadhesionstrength", "label": "coatingadhesionstrength" },
                        { "value": "coatingadhesionstrengthSd", "label": "coatingadhesionstrengthSd" },
                        { "value": "coatingadhesionstrengthUnit", "label": "coatingadhesionstrengthUnit" },
                        { "value": "surfacemorphologycharacterization", "label": "surfacemorphologycharacterization" },
                        { "value": "surfacemorphology", "label": "surfacemorphology" },
                        { "value": "surfacemorphologyphoto", "label": "surfacemorphologyphoto" }
                    ]
                }, {
                    value: '基本物理性能',
                    label: '基本物理性能',
                    children: [
                        { "value": "sampleserial", "label": "sampleserial" },
                        { "value": "samplename", "label": "samplename" },
                        { "value": "matspecies", "label": "matspecies" },
                        { "value": "density", "label": "density" },
                        { "value": "densityUnit", "label": "densityUnit" },
                        { "value": "meltingpoint", "label": "meltingpoint" },
                        { "value": "meltingpointUnit", "label": "meltingpointUnit" },
                        { "value": "phasetransitiontemperature", "label": "phasetransitiontemperature" },
                        { "value": "phasetransitiontemperatureUnit", "label": "phasetransitiontemperatureUnit" },
                        { "value": "crystallinity", "label": "crystallinity" },
                        { "value": "degreeofpolymerization", "label": "degreeofpolymerization" },
                        { "value": "phvalue", "label": "phvalue" },
                        { "value": "color", "label": "color" },
                        { "value": "capRatio", "label": "capRatio" },
                        { "value": "granularity", "label": "granularity" },
                        { "value": "granularitySd", "label": "granularitySd" },
                        { "value": "granularityUnit", "label": "granularityUnit" }
                    ]
                }, {
                    value: '体外表面形成',
                    label: '体外表面形成',
                    children: [
                        { "value": "sampleserial", "label": "sampleserial" },
                        { "value": "typeofsbf", "label": "typeofsbf" },
                        { "value": "immersiontime", "label": "immersiontime" },
                        { "value": "immersiontimeUnit", "label": "immersiontimeUnit" },
                        { "value": "accumulationpoint", "label": "accumulationpoint" },
                        { "value": "surfaceconstitutionserial", "label": "surfaceconstitutionserial" },
                        { "value": "surfaceelementcharacterization", "label": "surfaceelementcharacterization" },
                        { "value": "surfaceelementname", "label": "surfaceelementname" },
                        { "value": "surfaceelementrepresenttype", "label": "surfaceelementrepresenttype" },
                        { "value": "surfaceelementdate", "label": "surfaceelementdate" },
                        { "value": "surfaceelementerrorrange", "label": "surfaceelementerrorrange" }
                    ]
                }, {
                    "value": "体外XRD",
                    "label": "体外XRD",
                    "children": [
                        { "value": "sampleserial", "label": "sampleserial" },
                        { "value": "typeofsbf", "label": "typeofsbf" },
                        { "value": "immersiontime", "label": "immersiontime" },
                        { "value": "immersiontimeUnit", "label": "immersiontimeUnit" },
                        { "value": "typeofxrd", "label": "typeofxrd" },
                        { "value": "equipmentxrd", "label": "equipmentxrd" },
                        { "value": "xrdcharacterization", "label": "xrdcharacterization" },
                        { "value": "detectedphase", "label": "detectedphase" },
                        { "value": "jcpdsnumber", "label": "jcpdsnumber" },
                        { "value": "thetadegree", "label": "thetadegree" },
                        { "value": "millerIndicesHkl", "label": "millerIndicesHkl" },
                        { "value": "spectraxrd", "label": "spectraxrd" }
                    ]
                }, {
                    "value": "体外实验",
                    "label": "体外实验",
                    "children": [
                        { "value": "sampleserial", "label": "sampleserial" },
                        { "value": "samplename", "label": "samplename" },
                        { "value": "nucleationsite", "label": "nucleationsite" },
                        { "value": "typeofsbf", "label": "typeofsbf" },
                        { "value": "componentofsbf", "label": "componentofsbf" },
                        { "value": "sbfflowspeed", "label": "sbfflowspeed" },
                        { "value": "sbfflowspeedUnit", "label": "sbfflowspeedUnit" },
                        { "value": "immersiontime", "label": "immersiontime" },
                        { "value": "immersiontimeUnit", "label": "immersiontimeUnit" },
                        { "value": "formationofbonelikeapatiteCharacterization", "label": "formationofbonelikeapatiteCharacterization" },
                        { "value": "semresult", "label": "semresult" },
                        { "value": "semPhotos", "label": "semPhotos" },
                        { "value": "xrdPhase", "label": "xrdPhase" },
                        { "value": "xrdPhasecomposition", "label": "xrdPhasecomposition" },
                        { "value": "xrdPhotos", "label": "xrdPhotos" },
                        { "value": "ftirresult", "label": "ftirresult" },
                        { "value": "growthofapatite", "label": "growthofapatite" },
                        { "value": "gragegrowthofapatite", "label": "gragegrowthofapatite" }
                    ]
                }, {
                    "value": "文献数据来源",
                    "label": "文献数据来源",
                    "children": [
                        { "value": "documentserial", "label": "documentserial" },
                        { "value": "datasourceliteraturetype", "label": "datasourceliteraturetype" },
                        { "value": "datasourcepublicationname", "label": "datasourcepublicationname" },
                        { "value": "datasourcetitle", "label": "datasourcetitle" },
                        { "value": "datasourceauthors", "label": "datasourceauthors" },
                        { "value": "datasourceyear", "label": "datasourceyear" },
                        { "value": "datasourcevolume", "label": "datasourcevolume" },
                        { "value": "datasourceissue", "label": "datasourceissue" },
                        { "value": "datasourcestartpage", "label": "datasourcestartpage" },
                        { "value": "datasourceendpage", "label": "datasourceendpage" },
                        { "value": "datasourcearticleno", "label": "datasourcearticleno" },
                        { "value": "doi", "label": "doi" },
                        { "value": "wosnumber", "label": "wosnumber" },
                        { "value": "issn", "label": "issn" },
                        { "value": "isbn", "label": "isbn" },
                        { "value": "datasourceurl", "label": "datasourceurl" },
                        { "value": "proceedingspapermeeting", "label": "proceedingspapermeeting" },
                        { "value": "proceedingspaperyear", "label": "proceedingspaperyear" },
                        { "value": "proceedingspaperlocation", "label": "proceedingspaperlocation" },
                        { "value": "datasourceabstract", "label": "datasourceabstract" },
                        { "value": "datasourcefulltext", "label": "datasourcefulltext" }
                    ]
                }, {
                    "value": "文献样品信息",
                    "label": "文献样品信息",
                    "children": [
                        { "value": "sampleserial", "label": "sampleserial" },
                        { "value": "samplename", "label": "samplename" },
                        { "value": "materialname", "label": "materialname" },
                        { "value": "sampleshape", "label": "sampleshape" },
                        { "value": "samplesizelength", "label": "samplesizelength" },
                        { "value": "samplesizewidth", "label": "samplesizewidth" },
                        { "value": "samplesizeheight", "label": "samplesizeheight" },
                        { "value": "samplesizediameter", "label": "samplesizediameter" },
                        { "value": "samplesizethickness", "label": "samplesizethickness" },
                        { "value": "samplesizeUnit", "label": "samplesizeUnit" },
                        { "value": "mattype", "label": "mattype" },
                        { "value": "matspecies", "label": "matspecies" },
                        { "value": "documentserial", "label": "documentserial" }
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
                            { "value": "Number_experiment", "label": "Number_experiment" },
                            { "value": "curve_id", "label": "curve_id" },
                            { "value": "graph_id", "label": "graph_id" },
                            { "value": "Q", "label": "Q" },
                            { "value": "Diameter_shrinkage_rate", "label": "Diameter_shrinkage_rate" },
                            { "value": "High_shrinkage_rate", "label": "High_shrinkage_rate" },
                            { "value": "porosity", "label": "porosity" },
                            { "value": "id", "label": "id" },
                            { "value": "source", "label": "source" },
                            { "value": "target", "label": "target" },
                            { "value": "weight", "label": "weight" },
                            { "value": "edge_id", "label": "edge_id" },
                            { "value": "idx", "label": "idx" },
                            { "value": "id_[0]", "label": "id_[0]" },
                            { "value": "temp", "label": "temp" },
                            { "value": "hold", "label": "hold" }
                        ]
                    }, {
                        "value": "几何结构",
                        "label": "几何结构",
                        "children": [
                            { "value": "Number_experiment", "label": "Number_experiment" },
                            { "value": "curve_id", "label": "curve_id" },
                            { "value": "graph_id", "label": "graph_id" },
                            { "value": "Q", "label": "Q" },
                            { "value": "Diameter_shrinkage_rate", "label": "Diameter_shrinkage_rate" },
                            { "value": "High_shrinkage_rate", "label": "High_shrinkage_rate" },
                            { "value": "porosity", "label": "porosity" },
                            { "value": "id", "label": "id" },
                            { "value": "source", "label": "source" },
                            { "value": "target", "label": "target" },
                            { "value": "weight", "label": "weight" },
                            { "value": "edge_id", "label": "edge_id" },
                            { "value": "idx", "label": "idx" },
                            { "value": "id_0", "label": "id_0" },
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
                            { "value": "Number_experiment", "label": "Number_experiment" },
                            { "value": "curve_id", "label": "curve_id" },
                            { "value": "graph_id", "label": "graph_id" },
                            { "value": "Q", "label": "Q" },
                            { "value": "Diameter_shrinkage_rate", "label": "Diameter_shrinkage_rate" },
                            { "value": "High_shrinkage_rate", "label": "High_shrinkage_rate" },
                            { "value": "porosity", "label": "porosity" }
                        ]
                    }, {
                        "value": "图片展示",
                        "label": "图片展示",
                        "children": [
                            { "value": "方孔", "label": "方孔" },
                            { "value": "金刚石", "label": "金刚石" },
                            { "value": "镜像金刚石", "label": "镜像金刚石" },
                            { "value": "面心八面体", "label": "面心八面体" },
                            { "value": "面心顶角", "label": "面心顶角" },
                            { "value": "体心顶角", "label": "体心顶角" }
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
                            { "value": "Pore_shape", "label": "Pore_shape" },
                            { "value": "Model_Porosity", "label": "Model_Porosity" },
                            { "value": "Specific_Surface_Area", "label": "Specific_Surface_Area" },
                            { "value": "Permeability", "label": "Permeability" },
                            { "value": "BV_TV", "label": "BV_TV" },
                            { "value": "Effective_Porosity", "label": "Effective_Porosity" }
                        ]
                    }, {
                        "value": "体外",
                        "label": "体外",
                        "children": [
                            { "value": "Pore_shape", "label": "Pore_shape" },
                            { "value": "Model_Porosity", "label": "Model_Porosity" },
                            { "value": "Specific_Surface_Area", "label": "Specific_Surface_Area" },
                            { "value": "Permeability", "label": "Permeability" },
                            { "value": "day", "label": "day" },
                            { "value": "ALP", "label": "ALP" },
                            { "value": "COL-1", "label": "COL-1" },
                            { "value": "OCN", "label": "OCN" },
                            { "value": "OPN", "label": "OPN" },
                            { "value": "RUNX-2", "label": "RUNX-2" }
                        ]
                    }]
            }],

            // 第一级表名
            select1: '',
            // 第二级表名
            select2: '',
            // 选择的图片
            select_pic: '',
            // 选择的列
            select_col: [],
            // 筛选
            checkAll: true,
            // 选择的一部分进行查询的列名
            checkedCols: [],
            // 用于选择——当前查询的表格的所有列名
            selected_cols: [],
            // 当对工艺优化的图片展示进行搜索时图片的来源
            src: '',
            // 当前查询的表格的所有列名
            cols: [],
            isIndeterminate: true,
            // 当前页的表格数据
            usedTableData: [],
            // 当前页码
            currentPage: 1,
            // 所有满足检索条件的数据 和 个数
            allData: [{}],
            cnt: 800,
        }
    },
    create() {

    },
    methods: {
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
        search() {
            console.log(this.select1);
            if (this.select1 != "类骨磷灰石" && this.select1 != "骨诱导" && this.select1 != "工艺优化" && this.select1 != "高通量实验") {
                this.$message({
                    message: '请选择检索的范围',
                    type: 'warning'
                });
            } else if (this.select1 == "工艺优化" && this.select2 == "图片展示") {
                // 下方搜索表格数据展示关闭
                this.showSearchDisplay = false;
                // 根据选项设置图片源
                console.log(this.select_pic);
                if (this.select_pic === "方孔") {
                    console.log("当前选择的是方孔");
                    this.src = require("../assets/方孔(1).jpg");
                } else if (this.select_pic === "金刚石") {
                    console.log("当前选择的是金刚石");
                    this.src = require("../assets/金刚石(1).jpg");
                } else if (this.select_pic === "镜像金刚石") {
                    console.log("当前选择的是镜像金刚石");
                    this.src = require("../assets/镜像金刚石(1).jpg");
                } else if (this.select_pic === "面心八面体") {
                    console.log("当前选择的是面心八面体");
                    this.src = require("../assets/面心八面体(1).jpg");
                } else if (this.select_pic === "面心顶角") {
                    console.log("当前选择的是面心顶角");
                    this.src = require("../assets/面心顶角(1).jpg");
                } else {
                    console.log("当前选择的是体心顶角");
                    this.src = require("../assets/体心顶角(1).jpg");
                }
                // 下方图片展示区域打开
                this.showPictureDisplay = true;
            }
            else {
                var _this = this;
                // 得到检索数据——allData
                axios({
                    method: "post",
                    url: '/api/basemodule/search/query',
                    data: {
                        select1: _this.select1,
                        select2: _this.select2,
                        select3: _this.search_input,
                        select4: _this.select_col
                    }
                }).then(function (resp) {
                    _this.allData = resp.data.data;
                    console.log(resp.data);
                    if (resp.data.code == 500) {
                        console.log("没有找到匹配记录");
                        _this.showSearchDisplay = false;
                        _this.$message('没有找到匹配记录');
                    } else if (resp.data.code == 0) {
                        // 根据 allData 计算得到 cnt(总数据条数) 和 cols(列名)
                        _this.cols = Object.keys(_this.allData[0]);
                        console.log(_this.cols);
                        _this.cnt = _this.allData.length;
                        // 将tabelData设置为allData的前10个数据(不足10个全部显示)
                        _this.usedTableData = _this.allData.slice(0, 10);

                        // 展示下方搜索区域内容
                        _this.showSearchDisplay = true;
                        // 第一次，默认全选
                        _this.checkedCols = _this.cols;
                        // 可供选择的列名（就是表格的全部列名）
                        _this.selected_cols = _this.cols;
                    }
                }).catch((error) => {
                    console.error('请求失败:', error)
                })
            }
        },
        search_by_cols() {
            var _this = this;
            // 根据选择的复选框进行搜索
            console.log(this.checkedCols)

            // 得到检索数据——allData
            axios({
                method: "post",
                url: '/api/basemodule/search/query',
                params: {
                    select1: _this.select1,
                    select2: _this.select2,
                    select3: _this.search_input,
                    select4: _this.checkedCols[0],
                }
            }).then(function (resp) {
                _this.allData = resp.data.data;
                console.log("select_by_cols");
                // 根据 allData 计算得到 cnt(总数据条数)
                _this.cnt = _this.allData.length;
                // 将tabelData设置为allData的前10个数据(不足10个全部显示)
                _this.usedTableData = _this.allData.slice(0, 10);
                console.log(_this.usedTableData);
            }).catch((error) => {
                console.error('请求失败:', error)
            })
        },
        display_cols() {
            this.cols = this.checkedCols;
        },
        handleChange(value) {
            console.log('选中的值：', value);
            this.select1 = value[0];
            this.select2 = value[1];
            if (this.select1 == "工艺优化" && this.select2 == "图片展示")
                this.select_pic = value[2];
            var tmp = [];
            if (typeof value[2] == 'string')
                tmp.push(value[2]);
            else
                tmp = value[2];
            this.select_col = tmp;
            console.log(this.select1);
            this.selected_cols = [];
        },
        // 筛选
        handleCheckAllChange(val) {
            this.checkedCols = val ? this.cols : [];
            this.isIndeterminate = false;
        },
        handleCheckedColsChange(value) {
            let checkedCount = value.length;
            this.checkAll = checkedCount === this.cols.length;
            this.isIndeterminate = checkedCount > 0 && checkedCount < this.cols.length;
        },
        //分页
        handleCurrentChange(val) {
            console.log(`当前页: ${val}`);
            this.currentPage = val;
            // 根据当前页重新确定新的 tabelData
            this.usedTableData = this.allData.slice(10 * (val - 1), 10 * val);
        },
        // 下载表格数据
        downloadAllData() {
            // 这里假设allTableData是包含所有查询结果的数据
            // 如果需要从服务器获取完整数据，可以在这里添加请求逻辑
            if (this.cnt === 0) {
                console.log(this.cnt);
                this.$message.warning('没有可下载的数据');
                return;
            }
            try {
                // 转换数据格式
                const exportData = this.allData.map(item => {
                    const formattedItem = {};
                    // 根据列名映射数据，确保导出的表头与表格一致
                    this.cols.forEach(col => {
                        formattedItem[col] = item[col];
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
        }
    },
}    
</script>

<style scoped>
::v-deep .el-input__inner.custom-height {
    height: 50px;
    /* 设置高度为 50px */
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
    font-family: 'Roboto', sans-serif;
}

/* 搜索栏 */
.search-container {
    width: 100%;
    height: 300px;
    background-image: url('../assets/bg3.jpg');
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-color: rgba(0, 0, 0, 0.5);
    /* 半透明黑色遮罩 */
    /* 添加 Flex 布局并居中 */
    display: flex;
    justify-content: center;
    /* 水平居中 */
    /*margin-top: 80px;*/
    align-items: center;
}

.search-bar {
    background-color: rgba(255, 255, 255, 0.7);
    padding: 50px 30px;
    border-radius: 8px;
    display: flex;
    width: 60%;
    /*margin-left: 20%;*/

}

.search-display {
    width: 100%;
    height: 800px;
    background-color: rgb(248, 245, 245);
    display: flex;
    flex-direction: column;
    /* 设置为垂直布局 */
}

/* 筛选 */
.konghang {
    height: 10px;
}

.filter-box {
    background-color: white;
    width: 70%;
    height: auto;
    margin-left: 15%;
    padding: 10px;
    display: flex;
    flex-direction: column;
    /* 设置为垂直布局 */
    align-items: flex-start;
}

.button-container {
    display: flex;
    margin-left: 90%;
    justify-content: flex-end;
    /* 将按钮推到容器的右侧 */
}

/* 检索数据展示 */
.search-data-box {
    padding: 15px;
    background-color: white;
    width: 70%;
    height: auto;
    margin-left: 15%;
}

/* 图片展示 */
.picture-block {
    width: 50%;
    margin-left: 25%;
    height: auto;
    border-radius: 0px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.pagination-container {
    margin-top: 16px;
    display: flex;
    align-items: center;
    justify-content: center; /* 水平居中 */
    gap: 20px; /* 替代按钮的margin-left，控制元素间距 */
}

</style>
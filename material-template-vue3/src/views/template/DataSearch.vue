<template>
  <div class="data-search-page">
    <Navbar />
    
    <!-- 搜索栏 -->
    <div class="search-container">
      <div class="search-bar">
        <el-cascader 
          :options="searchOptions" 
          @change="handleCascaderChange" 
          size="large" 
          :props="{ checkStrictly: true }"
          clearable
          placeholder="请选择搜索范围"
          style="flex: 1;"
        />
        <el-input 
          v-model="searchKeyword" 
          placeholder="输入具体检索内容..." 
          size="large"
          @keyup.enter="handleSearch"
          style="flex: 2; margin: 0 15px;"
        />
        <el-button 
          type="primary" 
          icon="Search" 
          @click="handleSearch" 
          size="large"
          style="width: 90px;"
        >
          搜索
        </el-button>
      </div>
    </div>

    <div class="search-display">
      <div class="konghang"></div>
      
      <!-- 选择在哪些列中进行查询 -->
      <div class="filter-box" v-if="showSearchDisplay">
        <el-checkbox 
          :indeterminate="isIndeterminate" 
          v-model="checkAll"
          @change="handleCheckAllChange"
        >
          全选
        </el-checkbox>
        <div style="margin: 10px 0;"></div>
        <el-checkbox-group 
          v-model="checkedCols" 
          @change="handleCheckedColsChange"
          style="display: flex; flex-wrap: wrap; justify-content: flex-start;"
        >
          <el-checkbox 
            v-for="col in selected_cols" 
            :label="col" 
            :key="col" 
            style="margin-right: 20px;"
          >
            {{ col }}
          </el-checkbox>
        </el-checkbox-group>
        <div style="margin: 10px 0;"></div>
        <div class="button-container">
          <el-button type="primary" @click="display_cols" round>确定</el-button>
        </div>
      </div>

      <!-- 展示搜索的数据 -->
      <div class="search-data-box" v-if="showSearchDisplay">
        <el-table 
          :data="usedTableData" 
          border 
          style="width: 100%;" 
          size="large"
          v-loading="loading"
        >
          <el-table-column 
            v-for="col in cols" 
            :prop="col" 
            :label="col" 
            :key="col" 
            width="200px"
            show-overflow-tooltip
          />
        </el-table>
        
        <!-- 分页和下载按钮 -->
        <div class="pagination-container">
          <el-pagination 
            @current-change="handleCurrentChange" 
            :current-page="currentPage" 
            :page-size="10"
            layout="total, prev, pager, next, jumper" 
            :total="cnt"
          />
          <el-button 
            type="primary" 
            icon="Download" 
            @click="downloadAllData"
            size="large"
            style="width: 80px; height: 35px;"
          >
            下载
          </el-button>
        </div>
      </div>
      
      <!-- 图片展示 -->
      <div class="picture-block" v-if="showPictureDisplay">
        <el-image :src="src">
          <template #placeholder>
            <div class="image-slot">
              加载中<span class="dot">...</span>
            </div>
          </template>
        </el-image>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { Search, Download } from '@element-plus/icons-vue'
import Navbar from '@/components/Navbar.vue'
import request from '@/utils/request'
import * as XLSX from 'xlsx'

const router = useRouter()

// 搜索的关键字
const searchKeyword = ref('')
// 是否显示表格搜索内容
const showSearchDisplay = ref(false)
// 是否展示图片搜索内容
const showPictureDisplay = ref(false)
// 第一级表名
const select1 = ref('')
// 第二级表名
const select2 = ref('')
// 选择的图片
const select_pic = ref('')
// 选择的列
const select_col = ref([])
// 筛选
const checkAll = ref(true)
// 选择的一部分进行查询的列名
const checkedCols = ref([])
// 用于选择——当前查询的表格的所有列名
const selected_cols = ref([])
// 当对工艺优化的图片展示进行搜索时图片的来源
const src = ref('')
// 当前查询的表格的所有列名
const cols = ref([])
const isIndeterminate = ref(true)
// 当前页的表格数据
const usedTableData = ref([])
// 当前页码
const currentPage = ref(1)
// 所有满足检索条件的数据 和 个数
const allData = ref([{}])
const cnt = ref(0)
const loading = ref(false)

// 搜索的选项（完整的选项树）
const searchOptions = ref([
  {
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
    children: [
      {
        value: '材料表面性能',
        label: '材料表面性能',
        children: [
          { value: "sampleserial", label: "sampleserial" },
          { value: "samplename", label: "samplename" },
          { value: "surfacetreatmentmethods", label: "surfacetreatmentmethods" },
          { value: "contactangle", label: "contactangle" },
          { value: "contactangleSd", label: "contactangleSd" },
          { value: "contactangleUnit", label: "contactangleUnit" },
          { value: "contactangleLiquidtype", label: "contactangleLiquidtype" },
          { value: "surfacetension", label: "surfacetension" },
          { value: "surfacetensionunit", label: "surfacetensionunit" },
          { value: "zetapotential", label: "zetapotential" },
          { value: "zetapotentialUnit", label: "zetapotentialUnit" },
          { value: "surfacepotentialsign", label: "surfacepotentialsign" },
          { value: "surfacepotential", label: "surfacepotential" },
          { value: "surfacepotentialUnit", label: "surfacepotentialUnit" },
          { value: "surfaceenergy", label: "surfaceenergy" },
          { value: "surfaceenergyUnit", label: "surfaceenergyUnit" },
          { value: "roughnesscharacterization", label: "roughnesscharacterization" },
          { value: "roughnessra", label: "roughnessra" },
          { value: "roughnessraSd", label: "roughnessraSd" },
          { value: "roughnessraUnit", label: "roughnessraUnit" },
          { value: "roughnessrarms", label: "roughnessrarms" },
          { value: "roughnessrarmsSd", label: "roughnessrarmsSd" },
          { value: "roughnessrarmsUnit", label: "roughnessrarmsUnit" },
          { value: "maximumroughnessdepth", label: "maximumroughnessdepth" },
          { value: "maximumroughnessdepthSd", label: "maximumroughnessdepthSd" },
          { value: "maximumroughnessdepthUnit", label: "maximumroughnessdepthUnit" },
          { value: "surfacemicrohardness", label: "surfacemicrohardness" },
          { value: "surfacemicrohardnessSd", label: "surfacemicrohardnessSd" },
          { value: "surfacemicrohardnessUnit", label: "surfacemicrohardnessUnit" },
          { value: "coatingadhesionstrength", label: "coatingadhesionstrength" },
          { value: "coatingadhesionstrengthSd", label: "coatingadhesionstrengthSd" },
          { value: "coatingadhesionstrengthUnit", label: "coatingadhesionstrengthUnit" },
          { value: "surfacemorphologycharacterization", label: "surfacemorphologycharacterization" },
          { value: "surfacemorphology", label: "surfacemorphology" },
          { value: "surfacemorphologyphoto", label: "surfacemorphologyphoto" }
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
        value: '体外表面形成',
        label: '体外表面形成',
        children: [
          { value: "sampleserial", label: "sampleserial" },
          { value: "typeofsbf", label: "typeofsbf" },
          { value: "immersiontime", label: "immersiontime" },
          { value: "immersiontimeUnit", label: "immersiontimeUnit" },
          { value: "accumulationpoint", label: "accumulationpoint" },
          { value: "surfaceconstitutionserial", label: "surfaceconstitutionserial" },
          { value: "surfaceelementcharacterization", label: "surfaceelementcharacterization" },
          { value: "surfaceelementname", label: "surfaceelementname" },
          { value: "surfaceelementrepresenttype", label: "surfaceelementrepresenttype" },
          { value: "surfaceelementdate", label: "surfaceelementdate" },
          { value: "surfaceelementerrorrange", label: "surfaceelementerrorrange" }
        ]
      }, {
        value: "体外XRD",
        label: "体外XRD",
        children: [
          { value: "sampleserial", label: "sampleserial" },
          { value: "typeofsbf", label: "typeofsbf" },
          { value: "immersiontime", label: "immersiontime" },
          { value: "immersiontimeUnit", label: "immersiontimeUnit" },
          { value: "typeofxrd", label: "typeofxrd" },
          { value: "equipmentxrd", label: "equipmentxrd" },
          { value: "xrdcharacterization", label: "xrdcharacterization" },
          { value: "detectedphase", label: "detectedphase" },
          { value: "jcpdsnumber", label: "jcpdsnumber" },
          { value: "thetadegree", label: "thetadegree" },
          { value: "millerIndicesHkl", label: "millerIndicesHkl" },
          { value: "spectraxrd", label: "spectraxrd" }
        ]
      }, {
        value: "体外实验",
        label: "体外实验",
        children: [
          { value: "sampleserial", label: "sampleserial" },
          { value: "samplename", label: "samplename" },
          { value: "nucleationsite", label: "nucleationsite" },
          { value: "typeofsbf", label: "typeofsbf" },
          { value: "componentofsbf", label: "componentofsbf" },
          { value: "sbfflowspeed", label: "sbfflowspeed" },
          { value: "sbfflowspeedUnit", label: "sbfflowspeedUnit" },
          { value: "immersiontime", label: "immersiontime" },
          { value: "immersiontimeUnit", label: "immersiontimeUnit" },
          { value: "formationofbonelikeapatiteCharacterization", label: "formationofbonelikeapatiteCharacterization" },
          { value: "semresult", label: "semresult" },
          { value: "semPhotos", label: "semPhotos" },
          { value: "xrdPhase", label: "xrdPhase" },
          { value: "xrdPhasecomposition", label: "xrdPhasecomposition" },
          { value: "xrdPhotos", label: "xrdPhotos" },
          { value: "ftirresult", label: "ftirresult" },
          { value: "growthofapatite", label: "growthofapatite" },
          { value: "gragegrowthofapatite", label: "gragegrowthofapatite" }
        ]
      }, {
        value: "文献数据来源",
        label: "文献数据来源",
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
        value: "文献样品信息",
        label: "文献样品信息",
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
    value: "工艺优化",
    label: "工艺优化",
    children: [
      {
        value: "烧结工艺",
        label: "烧结工艺",
        children: [
          { value: "Number_experiment", label: "Number_experiment" },
          { value: "curve_id", label: "curve_id" },
          { value: "graph_id", label: "graph_id" },
          { value: "Q", label: "Q" },
          { value: "Diameter_shrinkage_rate", label: "Diameter_shrinkage_rate" },
          { value: "High_shrinkage_rate", label: "High_shrinkage_rate" },
          { value: "porosity", label: "porosity" },
          { value: "id", label: "id" },
          { value: "source", label: "source" },
          { value: "target", label: "target" },
          { value: "weight", label: "weight" },
          { value: "edge_id", label: "edge_id" },
          { value: "idx", label: "idx" },
          { value: "id_0", label: "id_0" },
          { value: "temp", label: "temp" },
          { value: "hold", label: "hold" }
        ]
      }, {
        value: "几何结构",
        label: "几何结构",
        children: [
          { value: "Number_experiment", label: "Number_experiment" },
          { value: "curve_id", label: "curve_id" },
          { value: "graph_id", label: "graph_id" },
          { value: "Q", label: "Q" },
          { value: "Diameter_shrinkage_rate", label: "Diameter_shrinkage_rate" },
          { value: "High_shrinkage_rate", label: "High_shrinkage_rate" },
          { value: "porosity", label: "porosity" },
          { value: "id", label: "id" },
          { value: "source", label: "source" },
          { value: "target", label: "target" },
          { value: "weight", label: "weight" },
          { value: "edge_id", label: "edge_id" },
          { value: "idx", label: "idx" },
          { value: "id_0", label: "id_0" },
          { value: "x", label: "x" },
          { value: "y", label: "y" },
          { value: "z", label: "z" },
          { value: "feature", label: "feature" },
          { value: "active", label: "active" }
        ]
      }, {
        value: "力学性能评价",
        label: "力学性能评价",
        children: [
          { value: "Id", label: "Id" },
          { value: "Number_experiment", label: "Number_experiment" },
          { value: "curve_id", label: "curve_id" },
          { value: "graph_id", label: "graph_id" },
          { value: "Q", label: "Q" },
          { value: "Diameter_shrinkage_rate", label: "Diameter_shrinkage_rate" },
          { value: "High_shrinkage_rate", label: "High_shrinkage_rate" },
          { value: "porosity", label: "porosity" }
        ]
      }, {
        value: "图片展示",
        label: "图片展示",
        children: [
          { value: "方孔", label: "方孔" },
          { value: "金刚石", label: "金刚石" },
          { value: "镜像金刚石", label: "镜像金刚石" },
          { value: "面心八面体", label: "面心八面体" },
          { value: "面心顶角", label: "面心顶角" },
          { value: "体心顶角", label: "体心顶角" }
        ]
      }]
  }, {
    value: "高通量实验",
    label: "高通量实验",
    children: [
      {
        value: "体内",
        label: "体内",
        children: [
          { value: "Pore_shape", label: "Pore_shape" },
          { value: "Model_Porosity", label: "Model_Porosity" },
          { value: "Specific_Surface_Area", label: "Specific_Surface_Area" },
          { value: "Permeability", label: "Permeability" },
          { value: "BV_TV", label: "BV_TV" },
          { value: "Effective_Porosity", label: "Effective_Porosity" }
        ]
      }, {
        value: "体外",
        label: "体外",
        children: [
          { value: "Pore_shape", label: "Pore_shape" },
          { value: "Model_Porosity", label: "Model_Porosity" },
          { value: "Specific_Surface_Area", label: "Specific_Surface_Area" },
          { value: "Permeability", label: "Permeability" },
          { value: "day", label: "day" },
          { value: "ALP", label: "ALP" },
          { value: "COL-1", label: "COL-1" },
          { value: "OCN", label: "OCN" },
          { value: "OPN", label: "OPN" },
          { value: "RUNX-2", label: "RUNX-2" }
        ]
      }]
    }
  ])

const handleCascaderChange = (value) => {
  console.log('选中的值：', value)
  if (value && value.length > 0) {
    select1.value = value[0]
    if (value.length > 1) {
      select2.value = value[1]
    }
    if (select1.value === "工艺优化" && select2.value === "图片展示") {
      if (value.length > 2) {
        select_pic.value = value[2]
      }
    }
    const tmp = []
    if (value.length > 2) {
      if (typeof value[2] === 'string') {
        tmp.push(value[2])
      } else {
        tmp.push(...value[2])
      }
    }
    select_col.value = tmp
    selected_cols.value = []
  } else {
    select1.value = ''
    select2.value = ''
    select_pic.value = ''
    select_col.value = []
  }
}

const handleSearch = async () => {
  console.log(select1.value)
  if (select1.value !== "类骨磷灰石" && select1.value !== "骨诱导" && select1.value !== "工艺优化" && select1.value !== "高通量实验") {
    ElMessage.warning('请选择检索的范围')
    return
  }
  
  if (select1.value === "工艺优化" && select2.value === "图片展示") {
    // 下方搜索表格数据展示关闭
    showSearchDisplay.value = false
    // 根据选项设置图片源
    console.log(select_pic.value)
    const picMap = {
      "方孔": "/方孔.png",
      "金刚石": "/金刚石.png",
      "镜像金刚石": "/镜像金刚石.png",
      "面心八面体": "/面心八面体.png",
      "面心顶角": "/面心顶角.png",
      "体心顶角": "/体心顶角.png"
    }
    src.value = picMap[select_pic.value] || "/方孔.png"
    // 下方图片展示区域打开
    showPictureDisplay.value = true
  } else {
    loading.value = true
    try {
      // 调用真实的搜索API
      const response = await request.post('/basemodule/search/query', {
        select1: select1.value,
        select2: select2.value,
        select3: searchKeyword.value,
        select4: select_col.value
      })
      
      if (response.data?.code === 500) {
        console.log("没有找到匹配记录")
        showSearchDisplay.value = false
        ElMessage.warning('没有找到匹配记录')
      } else if (response.data?.code === 0 && response.data?.data) {
        // 根据 allData 计算得到 cnt(总数据条数) 和 cols(列名)
        allData.value = response.data.data
        if (allData.value.length > 0) {
          cols.value = Object.keys(allData.value[0])
          console.log('列名:', cols.value)
          cnt.value = allData.value.length
          // 将tableData设置为allData的前10个数据(不足10个全部显示)
          usedTableData.value = allData.value.slice(0, 10)
          
          // 展示下方搜索区域内容
          showSearchDisplay.value = true
          // 第一次，默认全选
          checkedCols.value = [...cols.value]
          // 可供选择的列名（就是表格的全部列名）
          selected_cols.value = [...cols.value]
          currentPage.value = 1
          ElMessage.success(`找到 ${cnt.value} 条匹配记录`)
        } else {
          showSearchDisplay.value = false
          ElMessage.info('没有找到匹配记录')
        }
      } else {
        showSearchDisplay.value = false
        ElMessage.warning('搜索返回异常，请稍后重试')
      }
    } catch (error) {
      console.error('请求失败:', error)
      ElMessage.error('搜索失败，请稍后重试')
      showSearchDisplay.value = false
    } finally {
      loading.value = false
    }
  }
}

const handleCheckAllChange = (val) => {
  checkedCols.value = val ? [...cols.value] : []
  isIndeterminate.value = false
}

const handleCheckedColsChange = (value) => {
  const checkedCount = value.length
  checkAll.value = checkedCount === cols.value.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < cols.value.length
}

const display_cols = () => {
  cols.value = checkedCols.value.length > 0 ? [...checkedCols.value] : []
  ElMessage.success('已应用列选择')
}

const handleCurrentChange = (val) => {
  console.log(`当前页: ${val}`)
  currentPage.value = val
  // 根据当前页重新确定新的 tableData
  usedTableData.value = allData.value.slice(10 * (val - 1), 10 * val)
}

const downloadAllData = () => {
  if (cnt.value === 0) {
    ElMessage.warning('没有可下载的数据')
    return
  }
  try {
    // 转换数据格式
    const exportData = allData.value.map(item => {
      const formattedItem = {}
      // 根据列名映射数据，确保导出的表头与表格一致
      cols.value.forEach(col => {
        formattedItem[col] = item[col] || ''
      })
      return formattedItem
    })
    
    // 创建工作簿和工作表
    const worksheet = XLSX.utils.json_to_sheet(exportData)
    const workbook = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(workbook, worksheet, '查询数据')
    
    // 生成包含当前日期的文件名
    const date = new Date()
    const fileName = `查询数据_${date.getFullYear()}${(date.getMonth()+1).toString().padStart(2, '0')}${date.getDate().toString().padStart(2, '0')}.xlsx`
    
    // 下载文件
    XLSX.writeFile(workbook, fileName)
    ElMessage.success('数据下载成功')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('数据下载失败，请稍后重试')
  }
}
</script>

<style lang="scss" scoped>
.data-search-page {
  min-height: 100vh;
  background-color: #f5f5f5;
}

/* 搜索栏 */
.search-container {
  width: 100%;
  height: 300px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  justify-content: center;
  align-items: center;
  padding-top: 60px;
}

.search-bar {
  background-color: rgba(255, 255, 255, 0.9);
  padding: 30px;
  border-radius: 8px;
  display: flex;
  width: 70%;
  gap: 15px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.search-display {
  width: 100%;
  min-height: 600px;
  background-color: rgb(248, 245, 245);
  display: flex;
  flex-direction: column;
}

/* 筛选 */
.konghang {
  height: 10px;
}

.filter-box {
  background-color: white;
  width: 70%;
  height: auto;
  margin: 0 auto 20px;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

.button-container {
  display: flex;
  width: 100%;
  justify-content: flex-end;
  margin-top: 10px;
}

/* 检索数据展示 */
.search-data-box {
  padding: 20px;
  background-color: white;
  width: 70%;
  height: auto;
  margin: 0 auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

/* 图片展示 */
.picture-block {
  width: 50%;
  margin: 20px auto;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  
  .image-slot {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    height: 200px;
    background: #f5f7fa;
    color: #909399;
  }
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}
</style>

<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" 
    xmlns:ead="urn:isbn:1-931666-22-9"
    xmlns:foo="https://library.columbia.edu/foo"
    xpath-default-namespace="urn:isbn:1-931666-22-9"
    exclude-result-prefixes="xs"
    version="2.0">
    
    <!-- This stylesheet audits EAD files for DACS compliance and other issues and returns errors/warnings in the message output stream. It replicates the deprecated CUL schematron, making use of some XSLT abilities not available in Schematron. The stylesheet is called by the validate_as_eads.py script as part of daily reporting on finding aid data from ArchivesSpace. 2020-06-05 dwh2128.   -->
    
    <xsl:output method="text" indent="no"/>
    
    <xsl:template match ='ead'>
        <!-- put here all the elements of which to check children... -->
        <xsl:apply-templates select="archdesc" mode="eval"/>
        <xsl:apply-templates select="archdesc/did" mode="eval"/>
        <xsl:apply-templates select="//*/@authfilenumber" mode="eval"/>
        <xsl:apply-templates select="//c" mode="eval"/>
        <xsl:apply-templates select="//container" mode="eval"/>  
        <xsl:apply-templates select="//unittitle | //persname | //corpname | //famname" mode="eval"/>
        <xsl:apply-templates select="//unitdate" mode="eval"/>
        <xsl:apply-templates select="//extref/@*:href" mode="eval"/>
    </xsl:template>
  
 
  
    <!--  For each context called by top template, create a template and use if statements for each test.-->
    
    <xsl:template match="@authfilenumber" mode="eval">
        <!-- TODO: add here the regex test for authority URIs, per acfa-195.      -->
        <!-- TEST THIS! -->
        
  
            <xsl:if test="not(matches(.,'^https?://(vocab\.getty\.edu/page/aat/\S+\d+|id\.worldcat\.org/fast/\S+\d+|id\.loc\.gov/authorities/names/\S+\d+|id\.loc\.gov/authorities/subjects/\S+\d+|id\.loc\.gov/authorities/genreForms/\S+\d+|id\.loc\.gov/vocabulary/countries/\w+|id\.loc\.gov/entities/providers/[\da-z]+)$'))">
                   
   
                       <xsl:call-template name="errorMsg">
                           <xsl:with-param name="tag">authorities</xsl:with-param>
                           <xsl:with-param name="errStr">@authfilenumber '<xsl:value-of select="."/>' is not correctly formed. </xsl:with-param>
                       </xsl:call-template> 
                   
            </xsl:if>
         
        

    </xsl:template>
    

    <xsl:template match="archdesc" mode="eval">
        <!--  Test the presence of required elements in <did>      -->
        <xsl:if test="not(scopecontent)">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">archdesc</xsl:with-param>
                <xsl:with-param name="errStr">archdesc must have scope and content element.</xsl:with-param>
            </xsl:call-template>
        </xsl:if>
        
        <xsl:if test="not(accessrestrict)">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">archdesc</xsl:with-param>
                <xsl:with-param name="errStr">archdesc must have at least one accessrestrict child element.</xsl:with-param>
            </xsl:call-template>
        </xsl:if>
        
              
    </xsl:template>
    
    
    <xsl:template match="archdesc/did" mode="eval">
<!--  Test the presence of required elements in <did>      -->

        <xsl:if test="not(langmaterial)">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">archdesc</xsl:with-param>
                <xsl:with-param name="errStr">did must contain langmaterial.</xsl:with-param>
            </xsl:call-template>
        </xsl:if>
        
        <xsl:if test="not(origination)">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">archdesc</xsl:with-param>
                <xsl:with-param name="errStr">did must contain origination.</xsl:with-param>
            </xsl:call-template>
        </xsl:if>
 
        <xsl:if test="not(unitdate)">
            
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">archdesc</xsl:with-param>
                <xsl:with-param name="errStr">did must contain unitdate.</xsl:with-param>
            </xsl:call-template>
        </xsl:if>
        
        <xsl:if test="not(unitid)">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">archdesc</xsl:with-param>
                <xsl:with-param name="errStr">did must contain unitid.</xsl:with-param>
            </xsl:call-template>
        </xsl:if>
        
        <xsl:if test="not(physdesc)">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">archdesc</xsl:with-param>
                <xsl:with-param name="errStr">did must contain physdesc.</xsl:with-param>
            </xsl:call-template>
        </xsl:if>
        
        <xsl:if test="not(origination/persname or origination/corpname or origination/famname)">
            
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">archdesc</xsl:with-param>
                <xsl:with-param name="errStr">did/origination must have at least one of persname, corpname, or famname as child element.</xsl:with-param>
            </xsl:call-template>
        </xsl:if>
        
        
    </xsl:template>
  
 
    
  <!-- Model of c element -->  
    <xsl:template match="c" mode="eval">
         <xsl:if test="count(did/container) &gt; 3">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">component</xsl:with-param>
                <xsl:with-param name="errStr">c[@id="<xsl:value-of select="@id"/>"] contains more than 3 container elements.</xsl:with-param>
            </xsl:call-template> 
        </xsl:if>

 
        <xsl:if test="count(did/unittitle) &gt; 1">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">component</xsl:with-param>
                <xsl:with-param name="errStr">c[@id="<xsl:value-of select="@id"/>"] contains more than 1 unittitle.</xsl:with-param>
            </xsl:call-template> 
        </xsl:if>
        
        
        
        <xsl:if test="@level='series' and c[@level='series']">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">component</xsl:with-param>
                <xsl:with-param name="errStr">c[@id="<xsl:value-of select="@id"/>"] has series nested inside series.</xsl:with-param>
            </xsl:call-template> 
        </xsl:if>
        
        <xsl:if test="@level='subseries' and not(parent::c[@level='series'])">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">component</xsl:with-param>
                <xsl:with-param name="errStr">c[@id="<xsl:value-of select="@id"/>"] is a subseries NOT nested inside a series.</xsl:with-param>
            </xsl:call-template> 
        </xsl:if>

        <xsl:if test="@level='file' and not(parent::c)">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">component</xsl:with-param>
                <xsl:with-param name="errStr">c[@id="<xsl:value-of select="@id"/>"] is a file not a child of another c.</xsl:with-param>
            </xsl:call-template> 
        </xsl:if>
        

    </xsl:template>     
    
   
   
   <xsl:template match="container" mode="eval">
       <xsl:if test="not(normalize-space(.))">
           <xsl:call-template name="errorMsg">
               <xsl:with-param name="tag">component</xsl:with-param>
               <xsl:with-param name="errStr">c[@id="<xsl:value-of select="ancestor::c[1]/@id"/>"]//<xsl:value-of select="name(.)"></xsl:value-of> contains no text.</xsl:with-param>
           </xsl:call-template> 
       </xsl:if>
       
   </xsl:template>
   
<!-- Flag elements with no text.  -->
    <xsl:template match="unittitle | persname | corpname | famname" mode="eval">
        <xsl:if test="not(normalize-space(.))">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">data</xsl:with-param>
                <xsl:with-param name="errStr"><xsl:value-of select="name()"></xsl:value-of> contains no text.</xsl:with-param>
            </xsl:call-template> 
        </xsl:if>
        
    </xsl:template>
   
   
   
    <xsl:template match="unitdate" mode="eval">
        <xsl:if test="not(ancestor::did)">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">structure</xsl:with-param>
                <xsl:with-param name="errStr"><xsl:value-of select="name()"/>  must be a descendant of did.</xsl:with-param>
            </xsl:call-template> 
        </xsl:if>
        
    </xsl:template>
   
   
    <xsl:template match="extref/@*:href" mode="eval">
        <!-- Test for links to .xls|.xlsx|.pdf over http that may be blocked by browser. -->
        <xsl:if test="matches(.,'\s?http:.*\.(xlsx?|pdf)\s?')">
            <xsl:call-template name="errorMsg">
                <xsl:with-param name="tag">data</xsl:with-param>
                <xsl:with-param name="errStr">extref has insecure link to binary file: <xsl:value-of select="."/></xsl:with-param>
            </xsl:call-template> 
        </xsl:if>
    </xsl:template>
    
   
    <!-- ################# -->
  
  

<xsl:template name="errorMsg">
    <!-- call with $errStr and $tag para -->
    <xsl:param name="errStr"/>
    <xsl:param name="tag"/>
    <xsl:text>⚠ </xsl:text>
    <xsl:value-of select="$errStr"/>
    <xsl:text> XPath: </xsl:text>
    <xsl:value-of select="foo:generateXPath(.)"/>
    <xsl:text> {</xsl:text>
    <xsl:value-of select="$tag"/>
    <xsl:text>}</xsl:text>
    <xsl:text>
</xsl:text>
    
</xsl:template>


    <xsl:function name="foo:generateXPath"  >
        <!-- Function to return unique XPATH expression for current node. -->
        <xsl:param name="pNode" as="node()"/>
        <!--
        <xsl:value-of select="$pNode/ancestor-or-self::*/concat(name(),
            '[',
            count(preceding-sibling::self) + 1,']')" separator="/"/>
        -->
        <xsl:for-each select="$pNode/ancestor-or-self::*">
        <xsl:text>/</xsl:text>
            <xsl:variable name="nodeName"><xsl:value-of select="name()"></xsl:value-of></xsl:variable>
            <xsl:value-of select="$nodeName"/>
            <xsl:text>[</xsl:text>
            <xsl:value-of select="count(preceding-sibling::*[name() = $nodeName]) + 1"/>
            <xsl:text>]</xsl:text>

        </xsl:for-each>
    </xsl:function>
</xsl:stylesheet>
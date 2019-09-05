<?xml version="1.0" encoding="UTF-8"?>
<!--   Use to extract file-level information from a finding aid EAD. Result is a pipe-delimited table.
    
Optional parameters:
  * series_scope (integer): the sequential number of a series to process. Default 0 causes all series to be processed.
  * subject: Term to describe type of material (default = AUDIO RECORDINGS)
-->

<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xpath-default-namespace="urn:isbn:1-931666-22-9"
    exclude-result-prefixes="xs" version="2.0">
    <xsl:output omit-xml-declaration="yes" method="text"/>
    <xsl:strip-space elements="*"/>
    
    <!-- Optionally limit scope to a particular series (default 0 means process all series) -->
    <xsl:param name="series_scope" as="xs:integer">0</xsl:param>
    
    <xsl:param name="form">AUDIO RECORDINGS</xsl:param>
    <!-- <xsl:param name="form">VIDEO RECORDINGS</xsl:param>-->
    
    
    <xsl:variable name="delim1">|</xsl:variable>
    
    <xsl:variable name="lf">
        <xsl:text>&#xA;</xsl:text>
    </xsl:variable>
    
    <xsl:variable name="heads"
        >collection_name|bib_id|rights|restrictions|repo_code|series_title|subseries_title|parent_file_title|ref_id|unittitle|unitdate|origination|box_num|container2|extent_number|extent|physfacet|form|scopenote|language|suggested_file_name</xsl:variable>
    
    
    
    <xsl:template match="ead">
        
        <!-- Insert header row (defined above) -->
        <xsl:value-of select="$heads"/>
        <xsl:value-of select="$lf"/>
        
        <xsl:choose>
            <xsl:when test="$series_scope != 0">
                <!-- if $series_scope selects a particular series, only process that series -->
                <xsl:apply-templates select="/ead/archdesc/dsc/c[$series_scope]//c[@level = 'file']"
                />
            </xsl:when>
            
            <xsl:otherwise>
                <xsl:apply-templates select="//c[@level = 'file']"/>
            </xsl:otherwise>
        </xsl:choose>
        
    </xsl:template>
    
    
    
    
    <xsl:template match="c[@level = 'file']">
        
        <!--       set fixed variables  -->
        <xsl:variable name="collection_name">
            <xsl:value-of select="normalize-space(//archdesc/did/unittitle)"/>
        </xsl:variable>
        <xsl:variable name="bib_id">
            <xsl:value-of select="normalize-space(//archdesc/did/unitid[1])"/>
        </xsl:variable>
        <xsl:variable name="repo_code">
            <xsl:value-of select="(//eadheader/eadid/@mainagencycode)"/>
        </xsl:variable>
        <xsl:variable name="rights">
            <!--            DEFAULT onsite -->
            <xsl:text>In copyright</xsl:text>
        </xsl:variable>
        <xsl:variable name="restrictions">
            <!--            DEFAULT TBD -->
            <xsl:text>Onsite access only</xsl:text>
        </xsl:variable>
        <xsl:variable name="creator">
            <!--            DEFAULT from collection-->
            <xsl:value-of select="normalize-space(//archdesc/did/origination)"/>
        </xsl:variable>
        <xsl:variable name="language">
            <xsl:value-of select="normalize-space(//archdesc/did/langmaterial/language)"/>
        </xsl:variable>
        
        
        
       
        
        <!--collection title-->
        <xsl:value-of select="$collection_name"/>
        <xsl:value-of select="$delim1"/>
        <!--bib ID-->
        <xsl:value-of select="$bib_id"/>
        <xsl:value-of select="$delim1"/>
        <!--rights-->
        <xsl:value-of select="$rights"/>
        <xsl:value-of select="$delim1"/>
        <!--restrictions-->
        <xsl:value-of select="$restrictions"/>
        <xsl:value-of select="$delim1"/>
        <!--repo -->
        <xsl:value-of select="$repo_code"/>
        <!--                  series location  -->
        <xsl:value-of select="$delim1"/>
        <xsl:choose>
            <xsl:when test="parent::c[@level = 'series']">
                <!-- grab series -->
                <xsl:value-of select="parent::c[@level = 'series']/did/unittitle"/>
                <xsl:value-of select="$delim1"/>
                <!-- blank subseries column  -->
                <xsl:text>No Subseries</xsl:text>
                <xsl:value-of select="$delim1"/>
                <xsl:text>No Parent File</xsl:text>
                <xsl:value-of select="$delim1"/>
            </xsl:when>
            <xsl:when test="parent::c[@level = 'subseries']">
                <!-- grab series and subseries-->
                <xsl:value-of
                    select="normalize-space(ancestor::c[@level = 'series'][1]/did/unittitle)"/>
                <xsl:value-of select="$delim1"/>
                <xsl:value-of
                    select="normalize-space(parent::c[@level = 'subseries']/did/unittitle)"/>
                <xsl:value-of select="$delim1"/>
                <xsl:text>No Parent File</xsl:text>
                <xsl:value-of select="$delim1"/>
            </xsl:when>
            <xsl:when test="parent::c[@level = 'file']">
                <!--  grab series and subseries and file -->
                <xsl:value-of
                    select="normalize-space(ancestor::c[@level = 'series'][1]/did/unittitle)"/>
                <xsl:value-of select="$delim1"/>
                <xsl:value-of
                    select="normalize-space(ancestor::c[@level = 'subseries'][1]/did/unittitle)"/>
                <xsl:value-of select="$delim1"/>
                <xsl:value-of select="normalize-space(parent::c[@level = 'file']/did/unittitle)"/>
                <xsl:value-of select="$delim1"/>
            </xsl:when>
            <xsl:otherwise>
                <!-- TODO: check this case for parallel structure -->
                <xsl:value-of select="$delim1"/>
                <xsl:text>CHECK HIERARCHY</xsl:text>
                <xsl:value-of select="$delim1"/>
                <xsl:value-of select="$delim1"/>
            </xsl:otherwise>
        </xsl:choose>
        <!--  as id -->
        <xsl:value-of select="substring-after(@id, 'aspace_')"/>
        <xsl:value-of select="$delim1"/>
        <!--  title -->
        <xsl:value-of select="normalize-space(did/unittitle)"/>
        <xsl:value-of select="$delim1"/>
        <!--  date -->
        <xsl:choose>
            <xsl:when test="did/unitdate[1]/text() = 'undated'">
                <xsl:text>uuuu</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="normalize-space(did/unitdate[1])"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="$delim1"/>
        <!--   creator  -->
        <xsl:choose>
            <xsl:when test="did/origination">
                <xsl:value-of select="normalize-space(did/origination)"/>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$creator"/>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="$delim1"/>
        <!-- box number -->
        <xsl:value-of select="normalize-space(did/container[@type = 'box'][1])"/>
        <xsl:value-of select="$delim1"/>
        <!-- folder/reel etc number -->
        <xsl:value-of select="normalize-space(did/container[2])"/>
        <xsl:value-of select="$delim1"/>
        <!-- extent_number -->
        <xsl:value-of select="substring-before(normalize-space(did/physdesc/extent), ' ')"/>
        <xsl:value-of select="$delim1"/>
        <!-- extent -->
        <xsl:value-of select="normalize-space(did/physdesc/extent)"/>
        <xsl:value-of select="$delim1"/>
        <!-- physfacet -->
        <xsl:value-of select="normalize-space(did/physdesc/physfacet)"/>
        <xsl:value-of select="$delim1"/>
        <!-- subject  -->
        <xsl:value-of select="$form"/>
        <xsl:value-of select="$delim1"/>
        <!-- scope note -->
        <xsl:for-each select="scopecontent/p">
            <xsl:value-of select="normalize-space(.)"/>
            <xsl:text> </xsl:text>
        </xsl:for-each>
        <xsl:value-of select="$delim1"/>
        <!-- language  -->
        <xsl:value-of select="$language"/>
        <xsl:value-of select="$delim1"/>
        <!-- suggested file name; includes test for dao, which indicates presence of previously digitized content     -->
        <xsl:choose>
            <xsl:when test="did/dao">
                <!--  dao indicator-->
                <xsl:text>PREVIOUSLY DIGITIZED: </xsl:text>
                <xsl:value-of select="did/dao[1]/@*:href"/>
                <xsl:value-of select="$lf"/>
            </xsl:when>
            <xsl:otherwise>
                <!--suggested file name-->
                <xsl:value-of select="substring-after(normalize-space($repo_code), 'US-NNC-')"/>
                <xsl:text>_</xsl:text>
                <xsl:value-of select="normalize-space($bib_id)"/>
                <xsl:text>_</xsl:text>
                <xsl:value-of select="normalize-space(did/container[@type = 'box'][1])"/>
                <xsl:text>_</xsl:text>
                <xsl:choose>
                    <xsl:when test="did/container[2]">
                        <xsl:value-of select="normalize-space(did/container[2])"/>
                    </xsl:when>
                    <xsl:otherwise>
                        <xsl:value-of select="position()"/>
                    </xsl:otherwise>
                </xsl:choose>  
                <xsl:value-of select="$lf"/>
            </xsl:otherwise>
        </xsl:choose>
        
        
        
    </xsl:template>
    
</xsl:stylesheet>

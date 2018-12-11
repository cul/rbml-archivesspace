<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:ead="urn:isbn:1-931666-22-9"
    xmlns:xlink="http://www.w3.org/1999/xlink" xpath-default-namespace="urn:isbn:1-931666-22-9"
    
    exclude-result-prefixes="xs" version="2.0">
    
    <xsl:output method="text"/>
    

    <xsl:variable name="lf"><xsl:text>
</xsl:text>
    </xsl:variable>
    
    <xsl:variable name="delim1">|</xsl:variable>
    <xsl:variable name="delim2">;</xsl:variable>
       
    
    <!--    Provide file path ($filePath) of folder to scan for unpublished EADs. Output will be a list of file paths. -->
    <xsl:param name="filePath">/path/to/files/</xsl:param>
    
    
    <!--    This is where the column heads are drawn from. Should match process below.   -->
    <xsl:variable name="myHead">FileName|URI|Repo|Title|Status|HasDSC|CountContainers</xsl:variable>
   
    
    
    <xsl:template match="/">
        
        <xsl:value-of select="$myHead"/>     
        <xsl:value-of select="$lf"></xsl:value-of>
        


        <xsl:for-each select="collection(concat($filePath, '?select=*.xml;recurse=yes'))">
            
            <xsl:variable name="mypath" select="tokenize(base-uri(),'/')"/>
            
            <xsl:variable name="filename">
                <xsl:value-of select="$mypath[last()]"/>
            </xsl:variable>
            
 
            <!--            File Name -->
            <xsl:value-of select="$filename"/>
            <xsl:value-of select="$delim1"/>

            <!--            File Path -->
            <xsl:value-of select="base-uri()"/>
            <xsl:value-of select="$delim1"/>
            
            <!--            Repo -->
            <xsl:value-of select="ead/archdesc/did/unitid[1]/@repositorycode"/>
            <xsl:value-of select="$delim1"/>
            
            <!--            Title -->
            <xsl:value-of select="normalize-space(ead/archdesc/did/unittitle[1])"/> <xsl:value-of select="normalize-space(ead/archdesc/did/unitdate[1])"/> 
            <xsl:value-of select="$delim1"/>
            
            <!--            Status -->
            <xsl:value-of select="ead/eadheader/@findaidstatus"/>
            <xsl:value-of select="$delim1"/>
            
            <!--            Has DSC? -->
            <xsl:if test="normalize-space(ead/archdesc/dsc[1])">
                <xsl:text>Y</xsl:text>
            </xsl:if>
            <xsl:value-of select="$delim1"/>
            
            <!--            Count of containers -->
            <xsl:value-of select="count(//c)"/>
            <xsl:value-of select="$delim1"/>
            
            
             <xsl:value-of select="$lf"></xsl:value-of>

        </xsl:for-each>
        
    </xsl:template>
    
    
    
    <xsl:template match="col">
        <xsl:value-of select="label"/>
        <xsl:value-of select="$delim1"/>
    </xsl:template>
    
</xsl:stylesheet>

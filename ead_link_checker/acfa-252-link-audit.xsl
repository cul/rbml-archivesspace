<?xml version="1.0" encoding="UTF-8"?>
<!-- Transform batch of EAD to extract xlink info for auditing. -->
<!-- Output format: bibid|container_id|href|title|text -->
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns:xlink="http://www.w3.org/1999/xlink"
    xmlns:foo="https://library.columbia.edu/foo"
    exclude-result-prefixes="xs"
    version="2.0" xpath-default-namespace="urn:isbn:1-931666-22-9">
    
    <xsl:output method="text" indent="no"/>
    
    <xsl:param name="filePath">/Users/dwh2128/Documents/ACFA/exist-local/backups/cached_eads/ead_cache_20200729/</xsl:param> 
    
    
    <xsl:variable name="lf"><xsl:text>
</xsl:text>
    </xsl:variable>
    
    <xsl:variable name="delim1">|</xsl:variable>
    <xsl:variable name="delim2">;</xsl:variable>    
    
    
    
    <xsl:variable name="heads">bibid|container_id|href|title|text</xsl:variable>
    
    <xsl:template match ="/">
        <xsl:value-of select="$heads"/>
        <xsl:value-of select="$lf"/>
        
        
        <xsl:for-each select="collection(concat($filePath, '?select=*.xml;recurse=yes'))">
            <xsl:variable name="bibid">
<!--                <xsl:value-of select="/ead/eadheader/eadid"/>-->
                <xsl:value-of select="/ead/archdesc/did/unitid[1]"/>
            </xsl:variable>
            
            
<!--            
            <xsl:variable name="mypath" select="tokenize(base-uri(),'/')"/>
            
            <xsl:variable name="filename">
                <xsl:value-of select="$mypath[last()]"/>
            </xsl:variable>
-->            
            
            <xsl:for-each select="//*[@xlink:href]">
                                
                <xsl:value-of select="$bibid"/>
                <xsl:value-of select="$delim1"/>        
                <xsl:value-of select="ancestor::c[@id][1]/@id"/>
                <!--        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="foo:generateXPath(.)"/>
-->
                <xsl:value-of select="$delim1"/>
                <xsl:value-of select="@xlink:href"/>
                <xsl:value-of select="$delim1"/>
                <xsl:value-of select="normalize-space(@xlink:title)"/>
                <xsl:value-of select="$delim1"/>
                <xsl:value-of select="normalize-space(text()[1])"/>
                <xsl:value-of select="$lf"/>
                
                
            </xsl:for-each>
            
         </xsl:for-each>        
        
    </xsl:template>
    
    
    <xsl:template match='*[@xlink:href]'>
        <xsl:param name="bibid"/>
        <xsl:value-of select="$bibid"/>
        <xsl:value-of select="$delim1"/>        
        <xsl:value-of select="ancestor::c[@id][1]/@id"/>
<!--        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="foo:generateXPath(.)"/>
-->
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="@xlink:href"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="normalize-space(@xlink:title)"/>
        <xsl:value-of select="$delim1"/>
        <xsl:value-of select="normalize-space(text()[1])"/>
        <xsl:value-of select="$lf"/>
        
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
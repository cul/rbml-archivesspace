<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xpath-default-namespace="urn:isbn:1-931666-22-9"
    exclude-result-prefixes="xs" version="2.0">
    
    <xsl:output method="xml" encoding="utf-8" indent="yes"/>
    
    
    <!-- Source will be output from ead_merge.xsl -->
    
    
    
    <xsl:param name="theDate">
        <xsl:value-of select="format-date(current-date(), 
            '[Y0001]-[M01]-[D01]')"/>
    </xsl:param>
    
    <xsl:variable name="my_name">ead_cleanup_1.xsl</xsl:variable>
    
    <!-- Identity template -->
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    
    
    <xsl:template match="/">
        <!-- Some info about merge added at runtime.    -->
        <xsl:comment> 
    <xsl:text>File cleaned by </xsl:text><xsl:value-of select="$my_name"/><xsl:text> on </xsl:text>
    <xsl:value-of select="current-dateTime()"/>
        </xsl:comment>
        <xsl:text>&#xa;</xsl:text>
        
        <xsl:apply-templates/>
        
    </xsl:template>
    
    
    <!--     Delete empty p and other tags -->
    
    <xsl:template match="*[not(normalize-space(.))][not(@*)][not(ancestor::dsc)]"/>
    
    
    
    <!--    match physdesc/genreform and an existing scopecontent -->
    
    
    <xsl:template match="c[@level='file']/scopecontent[../did/physdesc/genreform]">
        <xsl:variable name="the_genreforms">
            <xsl:for-each select="../did/physdesc/genreform">
                <xsl:element name="p" namespace="urn:isbn:1-931666-22-9">
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:for-each>
        </xsl:variable>                

        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:apply-templates select="$the_genreforms"/>
            <xsl:apply-templates select="node()"/>
        </xsl:copy>
    </xsl:template>
    
    
    <!--    match physdesc/genreform where there is no existing scopecontent -->
    
    <xsl:template match="c[@level='file'][did/physdesc/genreform][not(scopecontent)]">
        <xsl:variable name="the_genreforms">
            <xsl:for-each select="did/physdesc/genreform">
                <xsl:element name="p" namespace="urn:isbn:1-931666-22-9">
                    <xsl:apply-templates/>
                </xsl:element>
            </xsl:for-each>
        </xsl:variable>                
        <xsl:copy>
            <xsl:apply-templates select="@*"/>
            <xsl:apply-templates select="node()"/>
            <xsl:element name="scopecontent" namespace="urn:isbn:1-931666-22-9">
                <xsl:apply-templates select="$the_genreforms"/>
            </xsl:element>
        </xsl:copy>
    </xsl:template>
    
    <!-- do nothing to delete the genreform element in the dsc-->
    <xsl:template match="genreform[ancestor::dsc]"/>
    
    
    
</xsl:stylesheet>
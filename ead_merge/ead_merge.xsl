<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:ead="urn:isbn:1-931666-22-9"
    xpath-default-namespace="urn:isbn:1-931666-22-9" exclude-result-prefixes="xs" version="2.0">

    <xsl:output method="xml" encoding="utf-8" indent="yes"/>


<!-- Stylesheet to merge one legacy EAD file with corresponding ArchivesSpace EAD file. The top-level data comes from AS and the dsc section comes from legacy, with specific modifications as needed. Parameters can select which collection-level elements are to be migrated from the legacy file to replace those in the AS export. Called once per file from script ead_merge.py. -->



    <!--  *** 1. Some Setup ***  -->

    <!--   Pass the path of the ArchivesSpace EAD files as param -->
    <xsl:param name="asXMLFolder">as</xsl:param>

    <!-- Params for migration of eadheader elements   -->
    <xsl:param name="m_revisiondesc">Y</xsl:param>

    <!-- Params for migration of archdesc elements   -->
    <xsl:param name="m_bioghist">N</xsl:param>
    <xsl:param name="m_scopecontent">N</xsl:param>
    <xsl:param name="m_otherfindaid">N</xsl:param>
    <xsl:param name="m_relatedmaterial">N</xsl:param>

    <!-- Params for migration of archdesc/did elements   -->
    <xsl:param name="m_abstract">N</xsl:param>


    <!-- Capture the <dsc> section of the source tree for later use. -->
    <xsl:variable name="the_dsc">
        <xsl:copy-of select="//dsc"/>
    </xsl:variable>


    <!-- Capture certain collection-level elements to migrate. -->

    <xsl:variable name="add_ins">

        <xsl:if test="$m_revisiondesc = 'Y'">
            <xsl:copy-of select="//revisiondesc"/>
        </xsl:if>
        <xsl:if test="$m_bioghist = 'Y'">
            <xsl:copy-of select="//archdesc/bioghist"/>
        </xsl:if>
        <xsl:if test="$m_scopecontent = 'Y'">
            <xsl:copy-of select="//archdesc/scopecontent"/>
        </xsl:if>
        <xsl:if test="$m_otherfindaid = 'Y'">
            <xsl:copy-of select="//archdesc/otherfindaid"/>
        </xsl:if>
        <xsl:if test="$m_relatedmaterial = 'Y'">
            <xsl:copy-of select="//archdesc/relatedmaterial"/>
        </xsl:if>
        <xsl:if test="$m_abstract = 'Y'">
            <xsl:copy-of select="//archdesc/did/abstract"/>
        </xsl:if>

    </xsl:variable>


    <xsl:template match="*" mode="list">
        <!-- Generate list of element names for reporting purposes. -->
        <xsl:value-of select="local-name(.)"/>
        <xsl:text> </xsl:text>
    </xsl:template>


    <!--  *** 2. Main document processing ***  -->



    <!-- Match root of source but we will push everything from the companion EAD file instead. -->
    <xsl:template match="/">


        <!-- Some info about merge added at runtime.    -->
        <xsl:comment> 
    <xsl:text>Merged EAD created on  </xsl:text>
    <xsl:value-of select="current-dateTime()"/>
        </xsl:comment>
        <xsl:text>.&#xa;</xsl:text>
        <xsl:comment> 
    <xsl:text>Legacy sections migrated: dsc </xsl:text>
<xsl:apply-templates select="$add_ins" mode="list"/>
</xsl:comment>

        <xsl:text>&#xa;</xsl:text>
        <xsl:text>&#xa;</xsl:text>

        <!--    Grab the BibID and select the file. -->
        <xsl:variable name="bibID" select="ead/archdesc/did/unitid[@type='clio'][1]"/>

        <!--    Find the associated AS EAD file to merge with. -->
        <xsl:variable name="filePath" select="concat($asXMLFolder, '/', $bibID,'_ead.xml')"/>

        <xsl:apply-templates select="document($filePath)" mode="asead"/>

    </xsl:template>



    <xsl:template match="dsc" mode="asead">
        <!-- For dsc of document, grab the dsc from the original source tree instead. -->
        <!--    TODO: This may no longer be needed. -->
        <xsl:apply-templates select="$the_dsc" mode="legacy"/>
    </xsl:template>


    <!--  *********  -->


    <!-- Here we insert migrated elements that belong in eadhearder that may not already be there. -->
    <xsl:template match="eadheader" mode="asead">
        <xsl:copy>
            <xsl:apply-templates mode="asead"/>

            <xsl:if test="not(revisiondesc)">
                <!--  If there is something captured, then insert it. Otherwise you are inserting nothing, which is OK. -->
                <xsl:apply-templates select="$add_ins/revisiondesc" mode="legacy"/>
            </xsl:if>
        </xsl:copy>
    </xsl:template>

    <!-- Here we insert migrated elements that belong in archdesc/did that may not already be there. -->
    <xsl:template match="did[not(ancestor::dsc)]" mode="asead">
        <xsl:copy>

            <!--  If there is something captured in $add_in, then insert it. -->

            <xsl:if test="not(abstract) and $add_ins/abstract">
                <xsl:call-template name="insertElement">
                    <xsl:with-param name="theElement">abstract</xsl:with-param>
                </xsl:call-template>
            </xsl:if>

            <xsl:apply-templates mode="asead"/>

        </xsl:copy>
    </xsl:template>



    <!-- Here we insert migrated elements that belong in archdesc that may not already be there. -->
    <xsl:template match="archdesc" mode="asead">
        <xsl:copy>
            <xsl:attribute name="level">collection</xsl:attribute>

            <!-- Work through the non-dsc stuff, so dsc will be at end of archdesc -->
            <xsl:apply-templates select="*[not(self::dsc)]" mode="asead"/>


            <xsl:if test="not(scopecontent) and $add_ins/scopecontent">
                <xsl:call-template name="insertElement">
                    <xsl:with-param name="theElement">scopecontent</xsl:with-param>
                </xsl:call-template>
            </xsl:if>


            <xsl:if test="not(bioghist) and $add_ins/bioghist">
                <xsl:call-template name="insertElement">
                    <xsl:with-param name="theElement">bioghist</xsl:with-param>
                </xsl:call-template>
            </xsl:if>


            <xsl:if test="not(otherfindaid) and $add_ins/otherfindaid">
                <xsl:call-template name="insertElement">
                    <xsl:with-param name="theElement">otherfindaid</xsl:with-param>
                </xsl:call-template>
            </xsl:if>

            <xsl:if test="not(relatedmaterial) and $add_ins/relatedmaterial">
                <xsl:call-template name="insertElement">
                    <xsl:with-param name="theElement">relatedmaterial</xsl:with-param>
                </xsl:call-template>
            </xsl:if>


            <!-- Now bring in the dsc. -->
            <xsl:apply-templates select="$the_dsc" mode="legacy"/>


        </xsl:copy>
    </xsl:template>


    <!-- Identity template (legacy) -->
    <xsl:template match="@*|node()" mode="legacy">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" mode="legacy"/>
        </xsl:copy>
    </xsl:template>


    <!-- Identity template (as) -->
    <xsl:template match="@*|node()" mode="asead">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()" mode="asead"/>
        </xsl:copy>
    </xsl:template>



    <!--  *** 3. Record-specific replacements/insertions ***  -->



    <!--Special collection-level stuff to optionally migrate replacing existing elements:  -->

    <xsl:template
        match="revisiondesc[not(ancestor::dsc)] |
        bioghist[not(ancestor::dsc)] | 
        scopecontent[not(ancestor::dsc)] | 
        otherfindaid[not(ancestor::dsc)] |
        abstract[not(ancestor::dsc)]
        "
        mode="asead">
        <xsl:call-template name="replaceElement">
            <xsl:with-param name="theElement">
                <xsl:value-of select="local-name(.)"/>
            </xsl:with-param>
        </xsl:call-template>
    </xsl:template>


    <!--  *********  -->


    <!-- Generalized template called to insert named element from Legacy into result tree, replacing what is in AS tree. -->
    <xsl:template name="replaceElement">
        <!-- This template is only called when matching an existing element in the AS data. Otherwise the parent templates dictate what is inserted from legacy.   -->
        <xsl:param name="theElement"/>
        <xsl:variable name="theName" as="xs:string" select="$theElement"/>
        <xsl:choose>
            <xsl:when test="$add_ins/*[ local-name() = $theName ]">
                <!--  There is something captured in the add_ins for this element to insert. -->
                <xsl:if test="count(preceding-sibling::*[local-name()=$theElement]) = 0">
                    <xsl:comment><xsl:value-of select="$theElement"/> inserted from legacy EAD.</xsl:comment>
                    <xsl:text>&#xa;</xsl:text>
                    <xsl:apply-templates select="$add_ins/*[ local-name() = $theName ]"
                        mode="legacy"/>
                    <!--  and omit the rest.-->
                </xsl:if>
            </xsl:when>
            <xsl:otherwise>
                <!--   We are keeping what's in AS as is. -->
                <xsl:copy>
                    <xsl:apply-templates mode="asead"/>
                </xsl:copy>
            </xsl:otherwise>
        </xsl:choose>

    </xsl:template>


    <xsl:template name="insertElement">
        <!-- Call this template to insert an element from legacy when there is none in AS. -->
        <xsl:param name="theElement"/>
        <xsl:variable name="theName" as="xs:string" select="$theElement"/>
        <xsl:text>&#xa;</xsl:text>
        <xsl:comment>Inserted <xsl:value-of select="$theName"/> from legacy EAD. </xsl:comment>
        <xsl:text>&#xa;</xsl:text>
        <xsl:apply-templates select="$add_ins/*[ local-name() = $theName ]" mode="legacy"/>

    </xsl:template>


    <!--  *** 4. Cleanup and modifications ***  -->


    <!-- Further changes to AS data (mode="asead") -->

    <xsl:template match="ead:eadid/@url" mode="asead">
        <xsl:attribute name="url">
            <xsl:analyze-string select="." regex="/ead//">
<xsl:matching-substring>/ead/</xsl:matching-substring>
                <xsl:non-matching-substring>
                    <xsl:value-of select="."/>
                </xsl:non-matching-substring>
            </xsl:analyze-string>
        </xsl:attribute>
    </xsl:template>


    <!-- Processing of migrated collection-level data, using mode="legacy" -->


    <xsl:template match="revisiondesc" mode="legacy">
        <xsl:copy>
            <xsl:apply-templates mode="legacy"/>
            <change>
                <date normal="2019-03-01">2019-03-01</date>
                <item>EAD was imported spring 2019 as part of the ArchivesSpace Phase II
                    migration.</item>
            </change>
        </xsl:copy>
    </xsl:template>


    <xsl:template match="titleproper[ancestor::eadheader]/num" mode="asead">
        <!-- omit -->
    </xsl:template>


    <!--  *********  -->

    <!-- Add processing of <dsc> section here, using mode="legacy" -->




</xsl:stylesheet>

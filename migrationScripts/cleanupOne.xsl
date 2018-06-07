<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:marc="http://www.loc.gov/MARC21/slim"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.loc.gov/MARC21/slim
    http://www.loc.gov/standards/marcxml/schema/MARC21slim.xsd" version="2.0"
    exclude-result-prefixes="marc xs xsi">
    <xsl:output method="xml" exclude-result-prefixes="#all"/>

    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <!--<!-\-   trailing periods  -\->
    <xsl:template
        match="marc:datafield/marc:subfield/text()[ends-with(., '.')]">
        <xsl:variable name="s" select="." />
        <xsl:value-of select="substring($s, 1, string-length($s) - 1)" />
    </xsl:template>
-->
    <!--    245 -->
    <!--  For 245 a, remove commas  -->
    <xsl:template match="marc:datafield[@tag='245']/marc:subfield[@code='a']/text()">
        <xsl:value-of select="translate(., ',' ,'')"/>
    </xsl:template>
    <!--  For 245 f, remove periods -->
<!--    <xsl:template match="marc:datafield[@tag='245']/marc:subfield[@code='f']/text()">
        <xsl:value-of select="translate(., '.' ,'')"/>
    </xsl:template>-->
    
    <!--  For 245 f ending in comma, remove final comma  -->
    <xsl:template match="marc:datafield[@tag='245']/marc:subfield[@code='f']/text()[ends-with(., '.,')]">
        <xsl:variable name="c" select="." />
        <xsl:value-of select="substring($c, 1, string-length($c) - 1)" />
    </xsl:template>
    
    <!--  For 245 g strip out all letters except s; punct except - -->
    <xsl:template match="marc:datafield[@tag='245']/marc:subfield[@code='g']/text()">
        <!--<xsl:variable name="c" select="." />-->
        <!--<xsl:value-of select="substring($c, 1, string-length($c) - 1)" />-->
        <xsl:value-of select="normalize-space(translate(., 'abcdefghijklmnopqrtuvwxyz.,[]()&amp;', ''))"/>
    </xsl:template>
  
    <!--  520 remove ind1=8 -->

    <xsl:template match="@ind1[parent::marc:datafield[@tag='520']]">
        <xsl:choose>
            <xsl:when test=". = '8'">
                <xsl:attribute name="ind1">
                    <xsl:value-of select="' '"/>
                </xsl:attribute>
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="." copy-namespaces="no"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>
    
<!--  concatenate second 555 fields into one -->
    <xsl:template match="marc:datafield[@tag='555']">
        <xsl:choose>
        <xsl:when test="../marc:datafield[@tag='555'][2]">
        <xsl:element name="datafield">
            <xsl:attribute name="tag">555</xsl:attribute>
            <xsl:attribute name="ind1"><xsl:value-of select="'0'"/></xsl:attribute>
            <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
            <xsl:element name="subfield">
                <xsl:attribute name="code">a</xsl:attribute>
                <xsl:value-of select="marc:subfield[@code='a']"/>
                <xsl:text>. </xsl:text>
                <xsl:value-of select="../marc:datafield[@tag='555'][2]/marc:subfield[@code='a']"/>
            </xsl:element>
        </xsl:element>
        </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="."/>
            </xsl:otherwise>
        </xsl:choose>
            
    </xsl:template>

    <!--    590 -->

    <!--  Template so 852 is handled in 590 rule if 590 exists     -->
    <xsl:template match="marc:datafield[@tag='852']">
        <xsl:choose>
            <xsl:when test="../marc:datafield[@tag='590']">
                <!--   do nothing     -->
            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="." copy-namespaces="no"/>
            </xsl:otherwise>
        </xsl:choose>


    </xsl:template>

    <xsl:template match="marc:datafield[@tag='590']">


        <xsl:choose>
            <!--  For backmehteff 590, move to 852$j -->
            <!--  Do we try to add the BA# numbers before this?      -->

            <xsl:when test="marc:subfield[@code='a'][contains(., 'BAR')]">
                <xsl:element name="datafield">
                    <xsl:attribute name="tag">852</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">j</xsl:attribute>
                        <xsl:value-of select="."/>
                    </xsl:element>
                    <xsl:copy-of select="../marc:datafield[@tag='852']/marc:subfield[@code='a']"/>
                    <xsl:copy-of select="../marc:datafield[@tag='852']/marc:subfield[@code='b']"/>
                    <xsl:copy-of select="../marc:datafield[@tag='852']/marc:subfield[@code='c']"/>
                    <xsl:copy-of select="../marc:datafield[@tag='852']/marc:subfield[@code='d']"/>
                    <xsl:copy-of select="../marc:datafield[@tag='852']/marc:subfield[@code='e']"/>
                    <xsl:copy-of select="../marc:datafield[@tag='852']/marc:subfield[@code='f']"/>
                    <xsl:copy-of select="../marc:datafield[@tag='852']/marc:subfield[@code='g']"/>
                </xsl:element>
            </xsl:when>
            <xsl:otherwise>
                <!--  For other 590s, move to 500$a. Also, copy 852
due to above -->
                <xsl:element name="datafield">
                    <xsl:attribute name="tag">500</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="."/>
                    </xsl:element>
                </xsl:element>
                <xsl:copy-of select="../marc:datafield[@tag='852']"/>
            </xsl:otherwise>

        </xsl:choose>




    </xsl:template>




    <!--  300  -->
    <xsl:template match="marc:record/marc:datafield[@tag='300']">

        <xsl:choose>
<!--            tests to do nothing when a's but no f's-->
            <xsl:when test="marc:subfield[@code='a'][3] and
                not(marc:subfield[@code='f'])">
                <xsl:copy-of select="." copy-namespaces="no"/>
<!--             do nothing where there are three sub a  -->
            </xsl:when>
            <xsl:when test="marc:subfield[@code='a'][2] and
                not(marc:subfield[@code='f'])">
                <!--             do nothing where there are two sub a  -->
                <xsl:copy-of select="." copy-namespaces="no"/>
            </xsl:when>
            <xsl:when test="marc:subfield[@code='a'] and
                not(marc:subfield[@code='f'])">
                <!--             do nothing where there is already only one sub a   -->
                <xsl:copy-of select="." copy-namespaces="no"/>
            </xsl:when>

            <!-- a f a case           -->
            <xsl:when test="marc:subfield[@code='a'][2] and
                not(marc:subfield[@code='f'][2])">
                
                <xsl:element name="datafield">
                    <xsl:attribute name="tag">300</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:copy-of select="marc:subfield[@code='a'][1]" copy-namespaces="no"/>
                    <xsl:variable name="concat1">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][2]/text(), ' ',
                            marc:subfield[@code='f'][1]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat1"/>
                    </xsl:element>

                    <xsl:copy-of select="marc:subfield[@code='b']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='c']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='e']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='g']" copy-namespaces="no"/>
                </xsl:element>
            </xsl:when>
            <!--   case 5 a and f pairs     -->
            
            <xsl:when test="marc:subfield[@code='a'][5] and
                marc:subfield[@code='f'][5]">
                <xsl:element name="datafield">
                    <xsl:attribute name="tag">300</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:variable name="concat1">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][1]/text(), ' ',
                            marc:subfield[@code='f'][1]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat1"/>
                    </xsl:element>
                    <xsl:variable name="concat2">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][2]/text(), ' ',
                            marc:subfield[@code='f'][2]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat2"/>
                    </xsl:element>
                    <xsl:variable name="concat3">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][3]/text(), ' ',
                            marc:subfield[@code='f'][3]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat3"/>
                    </xsl:element>
                    <xsl:variable name="concat4">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][4]/text(), ' ',
                            marc:subfield[@code='f'][4]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat4"/>
                    </xsl:element>
                    <xsl:variable name="concat5">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][5]/text(), ' ',
                            marc:subfield[@code='f'][5]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat5"/>
                    </xsl:element>
                    <xsl:copy-of select="marc:subfield[@code='b']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='c']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='e']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='g']" copy-namespaces="no"/>
                </xsl:element>
                
            </xsl:when>

            <!--   case 4 a and f pairs     -->
            
            <xsl:when test="marc:subfield[@code='a'][4] and
                marc:subfield[@code='f'][4]">
                <xsl:element name="datafield">
                    <xsl:attribute name="tag">300</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:variable name="concat1">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][1]/text(), ' ',
                            marc:subfield[@code='f'][1]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat1"/>
                    </xsl:element>
                    <xsl:variable name="concat2">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][2]/text(), ' ',
                            marc:subfield[@code='f'][2]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat2"/>
                    </xsl:element>
                    <xsl:variable name="concat3">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][3]/text(), ' ',
                            marc:subfield[@code='f'][3]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat3"/>
                    </xsl:element>
                    <xsl:variable name="concat4">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][4]/text(), ' ',
                            marc:subfield[@code='f'][4]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat4"/>
                    </xsl:element>
                    <xsl:copy-of select="marc:subfield[@code='b']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='c']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='e']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='g']" copy-namespaces="no"/>
                </xsl:element>
                
            </xsl:when>

            <!--   case 3 a and f pairs     -->

            <xsl:when test="marc:subfield[@code='a'][3] and
                marc:subfield[@code='f'][3]">
                <xsl:element name="datafield">
                    <xsl:attribute name="tag">300</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:variable name="concat1">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][1]/text(), ' ',
                            marc:subfield[@code='f'][1]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat1"/>
                    </xsl:element>
                    <xsl:variable name="concat2">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][2]/text(), ' ',
                            marc:subfield[@code='f'][2]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat2"/>
                    </xsl:element>
                    <xsl:variable name="concat3">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][3]/text(), ' ',
                            marc:subfield[@code='f'][3]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat3"/>
                    </xsl:element>
                    <xsl:copy-of select="marc:subfield[@code='b']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='c']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='e']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='g']" copy-namespaces="no"/>
                </xsl:element>

            </xsl:when>
            <!--   case 2 a and f pairs     -->
            <xsl:when test="marc:subfield[@code='a'][2] and
                marc:subfield[@code='f'][2]">

                <xsl:element name="datafield">
                    <xsl:attribute name="tag">300</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:variable name="concat1">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][1]/text(), ' ',
                            marc:subfield[@code='f'][1]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat1"/>
                    </xsl:element>
                    <xsl:variable name="concat2">
                        <xsl:value-of select="concat(marc:subfield[@code='a'][2]/text(), ' ',
                            marc:subfield[@code='f'][2]/text())"/>
                    </xsl:variable>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat2"/>
                    </xsl:element>
                    <xsl:copy-of select="marc:subfield[@code='b']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='c']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='e']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='g']" copy-namespaces="no"/>
                </xsl:element>
            </xsl:when>
            
            <!--   case 1 a and 2 f pair     -->
            <xsl:when test="marc:subfield[@code='a'] and
                marc:subfield[@code='f'][2]">
                <xsl:variable name="concat">
                    <xsl:value-of select="concat(marc:subfield[@code='a']/text(), ' ',
                        marc:subfield[@code='f'][1]/text(), ' ', marc:subfield[@code='f'][2]/text())"/>
                </xsl:variable>
                <xsl:element name="datafield">
                    <xsl:attribute name="tag">300</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat"/>
                    </xsl:element>
                    <xsl:copy-of select="marc:subfield[@code='b']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='c']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='e']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='g']" copy-namespaces="no"/>
                </xsl:element>
                
            </xsl:when>
            
            <!--   case 1 a and f pair     -->
            <xsl:when test="marc:subfield[@code='a'] and
                marc:subfield[@code='f']">
                <xsl:variable name="concat">
                    <xsl:value-of select="concat(marc:subfield[@code='a']/text(), ' ',
                        marc:subfield[@code='f']/text())"/>
                </xsl:variable>
                <xsl:element name="datafield">
                    <xsl:attribute name="tag">300</xsl:attribute>
                    <xsl:attribute name="ind1"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:attribute name="ind2"><xsl:value-of select="' '"/></xsl:attribute>
                    <xsl:element name="subfield">
                        <xsl:attribute name="code">a</xsl:attribute>
                        <xsl:value-of select="$concat"/>
                    </xsl:element>
                    <xsl:copy-of select="marc:subfield[@code='b']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='c']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='e']" copy-namespaces="no"/>
                    <xsl:copy-of select="marc:subfield[@code='g']" copy-namespaces="no"/>
                </xsl:element>

            </xsl:when>
            <xsl:otherwise>
                <xsl:copy-of select="." copy-namespaces="no"/>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


</xsl:stylesheet>

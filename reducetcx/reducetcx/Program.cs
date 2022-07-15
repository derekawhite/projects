using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Xml;
using System.IO;
using System.Text.RegularExpressions;

namespace reducetcx
{
    class Program
    {

        static void Main(string[] args)
        {

            if (args.Length < 1)
            {
                Console.WriteLine("Usage: reducetcx [input file] <trackpoints>\n");
                return;
            }

            String stXMLFile = args[0];
            String ext = Path.GetExtension(stXMLFile);
            String name = Path.GetFileNameWithoutExtension(stXMLFile);
            String dir = Path.GetDirectoryName(stXMLFile);
            if (dir != "")
                dir += Path.DirectorySeparatorChar;
            else
                dir = "." + Path.DirectorySeparatorChar;

            String stOutFile = dir + name + "out" + ext;

            XmlDocument m_xmlDoc = new XmlDocument();
            int nPoints = 0;
            int nMaxPoints = 0;

            if (args.Length >= 2)
                if (!int.TryParse(args[1], out nMaxPoints))
                    nMaxPoints = 0;

            XmlWriterSettings settings = new XmlWriterSettings();
            settings.Encoding = System.Text.Encoding.UTF8;
            settings.Indent = true;
            settings.OmitXmlDeclaration = true;
            settings.NewLineHandling = NewLineHandling.None;

            try
            {
                m_xmlDoc.Load(stXMLFile);
                XmlNodeList trackpoints;
                XmlNode track;
                string xmlns = m_xmlDoc.DocumentElement.Attributes["xmlns"].Value;
                XmlNamespaceManager nsmgr = null;

                if (xmlns != null)
                {
                    nsmgr = new XmlNamespaceManager(m_xmlDoc.NameTable);
                    nsmgr.AddNamespace("MsBuild", xmlns);
                    trackpoints = m_xmlDoc.SelectNodes("/MsBuild:TrainingCenterDatabase/MsBuild:Activities/MsBuild:Activity/MsBuild:Lap/MsBuild:Track/*", nsmgr);
                    track = m_xmlDoc.SelectSingleNode("/MsBuild:TrainingCenterDatabase/MsBuild:Activities/MsBuild:Activity/MsBuild:Lap/MsBuild:Track", nsmgr);
                }
                else
                {
                    trackpoints = m_xmlDoc.SelectNodes("/TrainingCenterDatabase/Activities/Activity/MsBuild/Track/*");
                    track = m_xmlDoc.SelectSingleNode("TrainingCenterDatabase/Activities/Activity/Lap/Track");
                }


                foreach (XmlNode trackpoint in trackpoints)
                {
                    XmlNode position;
                    if (nsmgr != null)
                        position = trackpoint.SelectSingleNode("MsBuild:Position", nsmgr);
                    else
                        position = trackpoint.SelectSingleNode("Position");

                    if (position != null)
                        nPoints++;
                    else
                        track.RemoveChild(trackpoint);  //Remove gaps
                }

                int nDivisor = 0;
                int nPoint = 0;

                if (nMaxPoints > 0)
                    nDivisor = nPoints / nMaxPoints;

                foreach (XmlNode trackpoint in trackpoints)
                {
                    XmlNode position;
                    if (nsmgr != null)
                        position = trackpoint.SelectSingleNode("MsBuild:Position", nsmgr);
                    else
                        position = trackpoint.SelectSingleNode("Position");

                    if (position != null)
                    {
                        nPoint++;
                        if (nDivisor > 0 && nPoint % nDivisor != 0)
                            track.RemoveChild(trackpoint);      //Reduces trackpoints
                    }
                }

                using (XmlWriter wr = XmlWriter.Create(stOutFile, settings))
                {
                    m_xmlDoc.Save(wr);
                    wr.Close();
                }

                Console.WriteLine(String.Format("Completed {0} : {1}\n", stXMLFile, stOutFile));
            }
            catch (Exception ex)
            {
                Console.WriteLine(String.Format("Error pasing file {0} : {1}\n", stXMLFile, ex.Message));
                return;
            }
        }
    }
}
    

#include "Getgeometry.h"
#include "GetGeometryForBimRv.h"
#include <memory>
#include "BmSWall.h"
#include "BrBrep.h"
#include "BrBrepFaceTraverser.h"
#include "BmGFilling.h"
#include "BmGStyleElem.h"
#include "BmMaterialElem.h"
#include <stdlib.h>
#include "BmFamilySymbol.h"
#include "BmGeomStepList.h"
#include "BmGeomTable.h"
#include "BmFamilyInstance.h"
#include "BmCategoryElem.h"
#include "Getparameters.h"
#include "BmRebarInSystem.h"
#include "BmRebar.h"

struct Vertex
{
    float x, y, z;

    friend bool operator==(const Vertex& i, const Vertex& j);
};

bool operator==(const Vertex& i, const Vertex& j)
{
    if ((i.x == j.x) && (i.y == j.y) && (i.z == j.z))
    {
        return TRUE;
    }
    else
    {
        return FALSE;
    };

};

float operator*(const Vertex& i, const Vertex& j)
{
    return ((i.x * j.x) + (i.y * j.y) + (i.z * j.z));
}

Vertex operator-(const Vertex& i, const Vertex& j)
{
    return Vertex{ (j.x - i.x) , (j.y - i.y) , (j.z - i.z) };
}

BOOLEAN checkvector(Vertex vector1, Vertex vector2)
{
    //y1z2-y2z1 = 0; z1x2-z2x1 = 0; x1y2-x2y1 = 0
    if ((abs(vector1.y * vector2.z - vector2.y * vector1.z) <= 20)        //5 mm offset
        and (abs(vector1.z * vector2.x - vector2.z * vector1.x) <= 20)    //5 mm offset
        and (abs(vector1.x * vector2.y - vector2.x * vector1.y) <= 20))   //5 mm offset
    {
        return true;
    }
    return false;
}

Vertex CrossProduct(Vertex pnt1, Vertex pnt2)
{
    float a1 = pnt1.x;
    float a2 = pnt1.y;
    float a3 = pnt1.z;

    float b1 = pnt2.x;
    float b2 = pnt2.y;
    float b3 = pnt2.z;

    return Vertex{ a2 * b3 - a3 * b2, a3 * b1 - a1 * b3, a1 * b2 - a2 * b1 };
}

float VectorLength(Vertex vector)
{
    return sqrt(vector.x * vector.x + vector.y * vector.y + vector.z * vector.z);
}

float AngleVector(Vertex vector1, Vertex vector2)
{
    float a1 = vector1.x;
    float a2 = vector1.y;
    float a3 = vector1.z;

    float b1 = vector2.x;
    float b2 = vector2.y;
    float b3 = vector2.z;

    float dot = a1 * b1 + a2 * b2 + a3 * b3;
    float cos = dot / (VectorLength(vector1) * VectorLength(vector2));
    return cos;
}


namespace FirstApp
{
    std::vector<std::vector<Vertex>> GeometryBox(float length, float thickness, float height, OdGeMatrix3d& Transform)
    {
        std::vector<std::vector<OdGePoint3d>> face_points{
            {OdGePoint3d{0,0,0}, OdGePoint3d{length, 0, 0}, OdGePoint3d{length,thickness,0}, OdGePoint3d{0,thickness,0}},
            {OdGePoint3d{0,0,height}, OdGePoint3d{length, 0, height}, OdGePoint3d{length,thickness,height}, OdGePoint3d{0,thickness,height}},
            {OdGePoint3d{0,0,0}, OdGePoint3d{length, 0, 0}, OdGePoint3d{length,0,height}, OdGePoint3d{0,0,height}},
            {OdGePoint3d{0,thickness,0}, OdGePoint3d{length,thickness,0}, OdGePoint3d{length,thickness,height}, OdGePoint3d{0,thickness, height}},
            {OdGePoint3d{0,0,0}, OdGePoint3d{0,thickness,0}, OdGePoint3d{0,thickness,height}, OdGePoint3d{0,0, height}},
            {OdGePoint3d{length,0,0}, OdGePoint3d{length,thickness,0}, OdGePoint3d{length,thickness,height}, OdGePoint3d{length,0, height}}
        };

        std::vector<std::vector<Vertex>> face_vertexs;
        for (std::vector<OdGePoint3d> face_point : face_points)
        {
            std::vector<Vertex> face_vertex;
            for (OdGePoint3d point : face_point)
            {
                point.transformBy(Transform);
                face_vertex.push_back(Vertex{ static_cast<float>(point.x * 304.8), static_cast<float>(point.y * 304.8), static_cast<float>(point.z * 304.8) });
            }
            face_vertexs.push_back(face_vertex);
        }
        return face_vertexs;
    }

    //check if the object is the door/window family instance
    //then get the 3d by parameters
    void CheckDoorWindowFamily(OdBmDatabasePtr& pDb, OdBmElementPtr& pElem, std::vector<std::vector<Vertex>>& face_points, OdBmGNodeIteratorPtr& iter)
    {
        if (!pElem->isKindOf(OdBmFamilyInstance::desc()))
        {
            return;
        }

        OdBmObjectId id = pElem->getHeaderCategoryId();
        OdBmCategoryElemPtr elem = id.safeOpenObject();
        if (elem->getCategory()->getName() != "Doors" and elem->getCategory()->getName() != "Windows")
        {
            return;
        }

        //get host
        OdBmFamilyInstancePtr pGElem = pElem;
        OdBmObjectId hostid = pGElem->getHostId();
        OdBmElementPtr host = hostid.safeOpenObject();
        //FirstApp::FA_Getparameters(pDb, host);

        //get type
        OdBmObjectId idtype = pElem->getTypeID();
        OdBmElementPtr typeelem = idtype.safeOpenObject();

        if (!idtype.isNull())
        {
            OdBmDatabasePtr m_pDb = pElem->getDatabase();
            FirstApp::FA_Getparameters(m_pDb, typeelem);
            for (OdBmGNodePtr pGNode : iter)
            {
                if (!(pGNode->isA() == OdBmGInstance::desc()))
                {
                    continue;
                }
                OdBmGInstancePtr pInstance = pGNode;               

                OdBmInstInfoBasePtr instInfoBasePtr = pInstance->getInstanceInfo();

                //get tranform
                OdGeMatrix3d Tranform = instInfoBasePtr->getTrf();

                face_points = GeometryBox(100, 100, 100, Tranform);
            }
        }
    }

    // Get geometry and write data to json file
    void FA_GetgeometryForBimRv(OdBmDatabasePtr pDb, OdUInt64 handle, OdBmGeometryOptions OptView, std::vector<std::vector<Vertex>>& faces_point)
    {
        OdBmElementPtr pElem = pDb->getObjectId(OdDbHandle(OdUInt64(handle))).safeOpenObject();
        // Get object's geometry
        OdBmObjectPtr pGeom;
        // Get geometry in 3D view
        pElem->getGeometry(OptView, pGeom);

        if (pGeom->isA() == OdBmGElement::desc())
        {
            OdBmGElement* pGElem = dynamic_cast<OdBmGElement*>(pGeom.get());

            // Get nodes
            OdBmGNodeIteratorPtr iter = pGElem->newGNodeIterator();
            OdBmGeometryPtrArray arrGeometries;
            std::vector<OdGeMatrix3dArray> arrTranform;
            OdGeMatrix3dArray Tranform;

            //std::vector<std::vector<Vertex>> faces_point;
            BOOLEAN is_ = false;
            // Get geometries
            FA_Get_Geometry_from_nodes(iter, OptView, arrGeometries, arrTranform, Tranform, is_);

            if (!arrGeometries.size())
            {
                OdBmGNodeIteratorPtr iter = pGElem->newGNodeIterator();
            }
            else
            {
                faces_point = FAGetpointsForBimrv(arrGeometries, arrTranform, handle);
            }            

            /*for (int i = 0; i < faces_point.size(); i++)
            {
                std::cout << "Face number: " << i << std::endl;
                for (Vertex vertex : faces_point[i])
                {
                    std::cout << vertex.x << " : " << vertex.y << " : " << vertex.z << std::endl;
                }
            }*/
            for (Vertex vertex : faces_point[0])
            {
                std::cout << vertex.x << " : " << vertex.y << " : " << vertex.z << std::endl;
            }
        }
    }

    

    std::vector<std::vector<Vertex>> FAGetpointsForBimrv(OdBmGeometryPtrArray& arrGeometries, std::vector<OdGeMatrix3dArray>& arrTranform, OdUInt64 handle)
    {
        std::vector<std::vector<Vertex>> face_points;
        std::vector<Vertex> empty_region_points;
        for (int i_geo = 0; i_geo < arrGeometries.size(); ++i_geo)
        {
            std::vector<Vertex> region_points;
            OdBmGeometryPtr pGeometry = arrGeometries[i_geo];
            OdGeMatrix3dArray Tranform = arrTranform[i_geo];
            OdBmFacePtrArray faces;
            pGeometry->getFaces(faces);

            //get face points
            int face_number = 0;
            for (OdBmFacePtrArray::iterator faceIt = faces.begin(); faceIt != faces.end(); ++faceIt)
            {
                face_number++;
                // Get first EdgeLoop of a face
                std::vector<Vertex> face_point;
                OdBmFacePtr pFace = *faceIt;

                GetPointFromFace(face_point, pFace, Tranform, region_points, false);

                //push back face points
                if (!face_point.empty())
                {
                    face_points.push_back(face_point);
                }
            }
        }

        return face_points;
    }

    void GetOpeningFromFace(std::vector<Vertex>& face_point, const OdBmFacePtr& pFace, const OdGeMatrix3dArray& Tranform)
    {
        OdBmGEdgeLoopPtr pFirstEdgeLoop = pFace->getFirstLoop();
        std::vector<Vertex> region_points;
        Vertex first_cross;
        BOOLEAN first_loop = true;
        if (pFirstEdgeLoop.isNull())
            return;

        OdBmGEdgeLoopPtr pNextEdgeLoop = pFirstEdgeLoop;

        while (!pNextEdgeLoop.isNull())
        {
            std::vector<Vertex> edge_points;
            // Get first edge in loop
            OdBmGEdgeBase* pNext = pNextEdgeLoop->getNext();
            while (!pNext->isLoop())
            {
                OdBmGEdge* pGEdge = dynamic_cast<OdBmGEdge*>(pNext);

                bool bForvardDir = true;
                int iEdgeForFace = 0;
                {
                    OdBmFace* pFaceInt = pGEdge->getFacesItem(iEdgeForFace);
                    if (pFaceInt != pFace.get())
                    {
                        pFaceInt = pGEdge->getFacesItem(1);
                        if (pFaceInt == pFace.get())
                        {
                            bForvardDir = false;
                            iEdgeForFace = 1;
                        }
                    }
                }

                if (pGEdge->isFlipped())
                    bForvardDir = !bForvardDir;

                // Get start and end points of the Edge
                OdGePoint3dArray egepnts;           // All the points
                OdGePoint3dArray sub_egepnts;       // Only first and edge points

                if (pGEdge->numberPoints() > 2)
                {
                    pGEdge->getFirstAndLastEdgeGePnts(sub_egepnts);
                    pGEdge->getInteriorEdgeGePnts(egepnts);
                    egepnts.insertAt(0, sub_egepnts[0]);
                    egepnts.insertAt(egepnts.size(), sub_egepnts[1]);
                }
                else
                {
                    OdString fisrtpoint;
                    OdString secondpoint;
                    pGEdge->getFirstAndLastEdgeGePnts(egepnts);
                }

                if (bForvardDir)
                {
                    for (int i = 0; i < egepnts.size(); i++)
                    {
                        AddPointToFace(egepnts[i], Tranform, region_points, edge_points);
                    }
                }
                else
                {
                    for (int i = egepnts.size() - 1; i >= 0; i--)
                    {
                        AddPointToFace(egepnts[i], Tranform, region_points, edge_points);
                    }
                }

                // Go to next edge in loop
                try
                {
                    pNext = pGEdge->getNextItem(iEdgeForFace);
                }
                catch (const OdError & err)
                {
                    break;
                }

            }//while (!pNext->isLoop())

            pNextEdgeLoop = pNextEdgeLoop->getNextLoop();

            if (first_loop)
            {
                first_cross = CrossProduct(edge_points[1]-edge_points[0], edge_points[2]- edge_points[0]);
                first_loop = false;
            }
            else
            {
                Vertex cur_cross = CrossProduct(edge_points[1] - edge_points[0], edge_points[2] - edge_points[0]);
                if (AngleVector(first_cross, cur_cross) > 0)
                {
                    for (int i = 0; i < edge_points.size(); i++)
                    {
                        face_point.push_back(edge_points[i]);
                    }
                }
            }
        }
    }


    void GetPointFromFace(std::vector<Vertex>& face_point, const OdBmFacePtr& pFace, const OdGeMatrix3dArray& Tranform, const std::vector<Vertex>& region_points, BOOLEAN print)
    {
        OdBmGEdgeLoopPtr pFirstEdgeLoop = pFace->getFirstLoop();

        if (pFirstEdgeLoop.isNull()) //it is possible
            return;

        Vertex lastvector{ 0,0,0 };

        OdBmGEdgeLoopPtr pNextEdgeLoop = pFirstEdgeLoop;
        while (!pNextEdgeLoop.isNull())
        {
            std::vector<Vertex> edge_points;
            // Get first edge in loop
            OdBmGEdgeBase* pNext = pNextEdgeLoop->getNext();
            while (!pNext->isLoop())
            {
                OdBmGEdge* pGEdge = dynamic_cast<OdBmGEdge*>(pNext);

                bool bForvardDir = true;
                int iEdgeForFace = 0;
                {
                    OdBmFace* pFaceInt = pGEdge->getFacesItem(iEdgeForFace);
                    if (pFaceInt != pFace.get())
                    {
                        pFaceInt = pGEdge->getFacesItem(1);
                        if (pFaceInt == pFace.get())
                        {
                            bForvardDir = false;
                            iEdgeForFace = 1;
                        }
                    }
                }

                if (pGEdge->isFlipped())
                    bForvardDir = !bForvardDir;

                // Get start and end points of the Edge
                OdGePoint3dArray egepnts;           // All the points
                OdGePoint3dArray sub_egepnts;       // Only first and edge points

                if (pGEdge->numberPoints() > 2)
                {
                    pGEdge->getFirstAndLastEdgeGePnts(sub_egepnts);
                    pGEdge->getInteriorEdgeGePnts(egepnts);
                    egepnts.insertAt(0, sub_egepnts[0]);
                    egepnts.insertAt(egepnts.size(), sub_egepnts[1]);
                }
                else
                {
                    OdString fisrtpoint;
                    OdString secondpoint;
                    pGEdge->getFirstAndLastEdgeGePnts(egepnts);
                }

                if (bForvardDir)
                {
                    for (int i = 0; i < egepnts.size(); i++)
                    {
                        AddPointToFace(egepnts[i], Tranform, region_points, edge_points);
                    }
                }
                else
                {
                    for (int i = egepnts.size() - 1; i >= 0; i--)
                    {
                        AddPointToFace(egepnts[i], Tranform, region_points, edge_points);
                    }
                }

                // Go to next edge in loop
                try
                {
                    pNext = pGEdge->getNextItem(iEdgeForFace);
                }
                catch (const OdError & err)
                {
                    break;
                }

            }//while (!pNext->isLoop())
            pNextEdgeLoop = pNextEdgeLoop->getNextLoop();

            //check if edgespoint im empty
            if (edge_points.empty())
            {
                //continue;
            }

            Vertex curvector = edge_points[edge_points.size() - 1] - edge_points[0];

            if (lastvector * curvector <= 0)
            {
                for (int i = 0; i < edge_points.size(); i++)
                {
                    face_point.push_back(edge_points[i]);
                }
            }
            else
            {
                for (int i = edge_points.size() - 1; i >= 0; i--)
                {
                    face_point.push_back(edge_points[i]);
                }
            }

            lastvector = curvector;


        }//while (!pNextEdgeLoop.isNull())

        //try to remove the middle point in line
        if (face_point.size() <= 4)
        {
            return;
        }

        int size = face_point.size();
        int i = 1;
        //while (i < size)
        {
            Vertex vector1;
            Vertex vector2;
            if (i == size - 1)
            {
                vector1 = face_point[i] - face_point[i - 1];
                vector2 = face_point[0] - face_point[i - 1];
            }
            else
            {
                vector1 = face_point[i] - face_point[i - 1];
                vector2 = face_point[i + 1] - face_point[i - 1];
            }

            if (checkvector(vector1, vector2))
            {
                //face_point.erase(face_point.begin() + i);
                //size = size - 1;
            }
            else
            {
                //s++i;
            }
        }

        //check the last point

    }

    void AddPointToFace(OdGePoint3d& point3d, const OdGeMatrix3dArray& Tranform, const std::vector<Vertex>& region_points, std::vector<Vertex>& edge_points)
    {
        for (int i = Tranform.size() - 1; i >= 0; i--)
        {
            point3d.transformBy(Tranform[i]);
        }

        Vertex vertex{ roundf((point3d.x)*304.8), roundf((point3d.y) * 304.8), roundf((point3d.z) * 304.8) };

        if (std::find(region_points.begin(), region_points.end(), vertex) != region_points.end())
        {
            return;
        }

        if (std::find(edge_points.begin(), edge_points.end(), vertex) == edge_points.end())
        {
            edge_points.push_back(vertex);
        }
    }
}

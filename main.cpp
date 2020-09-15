#include "main.h"
#include "BmFamilySymBol.h"
#include "BmCategoryElem.h"
#include "BmHostObjAttr.h"
#include "BmMaterialElem.h"
#include "BmFamilyInstance.h"
#include "BmNamedParam.h"
#include "BmFamilyParams.h"
#include "BmCompoundStructure.h"
#include "BmDPart.h"
#include "BmRebarInSystem.h"
#include "BmHeldRebarInstanceKey.h"
#include "BmRebarSystem.h"
#include "BmAreaReinforcementType.h"
#include "BmSymbolInfo.h"
#include "BmRebarSystemLayer.h"
#include "BmRebarBarType.h"
#include "BmRebar.h"
#include "BmRebarInstBase.h"
#include "BmRebarInstFreeForm.h"
#include "BmGCurve.h"
#include "BmBarGeometry.h"
#include "BmRamp.h"
#include "BmStairsElement.h"
#include "BmBaseRailing.h"
#include "BmGLine.h"
#include "BmVarSketch.h"
#include "BmPathRein.h"
#include "GetGeometryForBimRv.h"
#include "BmSWall.h"
#include "BmCurveDriver.h"
#include "BmFloor.h"
#include "Database/BmTransaction.h"
#include "Header.h"
#include <vector>
#include<iostream>
using namespace std;

class MyServices : public ExSystemServices, public OdExBimHostAppServices
{
protected:
    ODRX_USING_HEAP_OPERATORS(ExSystemServices);
};
struct Vertex
{
    float x, y, z;

    friend bool operator==(const Vertex& i, const Vertex& j);
};

int main()
{
    // Hard code for input Revit file
    OdString inFile(L"D:/Test8.rvt");


    // Create a custom Services object
    //////////////////////////////////////////////////////////////// Tạo đối tượng, 1 biến để sử dụng các hàm trong đó đọc file revit
    OdStaticRxObject<MyServices> svcs;

    // Initialize Runtime Extension environment
    ////////////////////////////////////////////////////////////////Khởi tạo môi trường
    odrxInitialize(&svcs);

    // Load module
    OdRxModule* pModule = ::odrxDynamicLinker()->loadModule(OdBmLoaderModuleName, false);

    // Create a BimRv database and fills it with input file content
    // tạo 1 biến chứa file revit; Đọc nó
    OdBmDatabasePtr pDb = svcs.readFile(inFile);

    // Create Filter Category Rule
    ////////////////////////////////////////////////////////////////Tạo danh mục filter; giống với tạo bộ lọc bên autocad
    OdBmFilterCategoryRulePtr pCategoryRule = OdBmFilterCategoryRule::createObject();
    // Add Category for filtering
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_StairsRailing, false));
    pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_Walls, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_Parts, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_StructuralColumns, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_Walls, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_Entourage, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_LightingFixtures, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_Doors, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_Windows, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_GenericModel, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_Entourage, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_RebarShape, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_AreaRein, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_Windows, false));
    //pCategoryRule->addCategory(pDb->getObjectId(OdBm::BuiltInCategory::OST_FaceSplitter, false));

    // Get element table iterator with filter
    //////////////////////////////////////////////////////////////// lọc tất cả các đối tượng với bộ lọc trên
    OdBmIterator<OdBmElementPtr>::pointer_type pElementsIt(pDb->newElemTableIterator()->filter(pCategoryRule).detach());

    // Get element Array
    // lấy tất cả các element từ bộ lọc phía trên
    OdBmElementPtrArray elements;
    for (OdBmElementPtr elem : pElementsIt->collect())
        //////////////////////////////////////////////////////////////// chỗ này chưa hiểu, nếu jj đây thì mới đẩy elemen vào mảng
        if (!elem->isKindOf(OdBmSymbol::desc()))
        {
            elements.push_back(elem);
        }

    // Get 3D view Option
    //////////////////////////////////////////////////////////////// tạo 1 Geometry 3D????
    OdBmGeometryOptions OptView = FirstApp::FA_Get3dviewoption(pDb);

    //////////////////////////////////////////////////////////////// Vòng lặp chạy qua các element, duyệt qua nó để lấy geometry, từ geometry lấy ra các thông số đặc trưng hình học
    std::vector<std::vector<Vertex>> faces_pointa;
    std::vector<PointP> list_point;
    for (OdBmElementPtr elem : elements)
    {
        OdUInt64 object_id = elem->objectId().getHandle();
        //if (object_id == 318365)
        {
            FirstApp::FA_GetgeometryForBimRv(pDb, object_id, OptView, faces_pointa);
            break;
        }
    }
    std::cout << "ok2" << std::endl;
    int ii = 0;
    for (Vertex vertex : faces_pointa[0])
    {
     //   std::cout << vertex.x << " : " << vertex.y << " : " << vertex.z << std::endl;
        list_point.push_back(PointP{ vertex.x,vertex.y,vertex.z,true,ii });
        ii++;
    }
    std::cout << "print list point" << std::endl;
    for (int i = 0; i < list_point.size(); i++)
    {
        std::cout<< list_point[i].stt <<" : " << list_point[i].x << " : " << list_point[i].y << " : " << list_point[i].z << std::endl;
    }
    MatPhang ABC;
    MatPhang ABCN;
    std::cout << "planABC" << std::endl;
    ABC = MatPhangABC(list_point[16],list_point[1],list_point[12]);
    ABCN = MPPhapTuyenABC(list_point[0], list_point[1], list_point[12]);
    std::cout << ABC.a << " , " << ABC.b << " , " << ABC.c<<" , " << ABC.d << std::endl;

    std::cout << "planABCN" << std::endl;
    std::cout << ABCN.a << " , " << ABCN.b << " , " << ABCN.c << " , " << ABCN.d << std::endl;
    std::cout << "Working" << std::endl;
    return 0;
}

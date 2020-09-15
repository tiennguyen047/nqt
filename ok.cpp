#include <iostream>
#include<math.h>
#include <vector>
#include <algorithm>
#include <sstream>
#include <iomanip>
#include<cmath>
using namespace std;
double Pi = 3.14159265358979;

struct MatPhang
{
public:
    double a, b, c, d;
};

struct PointP
{
public:
    double x, y, z;
    bool exist;
    int stt;
};

struct Vector
{
public:
    double x, y, z;
};
std::vector<PointP> boundary;
// Chiều dài vecter
double VectorLength(Vector AB) { return sqrt(AB.x * AB.x + AB.y * AB.y + AB.z * AB.z); }

//Lấy góc quay 2 Vecter
// = 0 khi 2 vecter cùng chiều
// = 90 khi 2 vecter Vuông góc
// = 180 khi 2 vecter ngược chiều
// Góc giữa 2 vecter luôn nhỏ hơn hoặc bằng 180 độ
double Angle2Vector(Vector vector1, Vector vector2)
{
    return 180 / Pi * acos((vector1.x * vector2.x + vector1.y * vector2.y + vector1.z * vector2.z) / (VectorLength(vector1) * VectorLength(vector2)));
}
void checkboundary(std::vector<PointP> listpoint, std::vector<PointP> boundary1)
{
    MatPhang abc;
    int n = listpoint.size();
    for (int i = 2; i < n; i++)
    {
        if (checkpoint_in_AB(listpoint[0], listpoint[1], listpoint[i]))
        {
            abc = MatPhangABC(listpoint[0], listpoint[1], listpoint[i++]);
        }
        else
        {
            abc = MatPhangABC(listpoint[0], listpoint[1], listpoint[i]);
            break;
        }
    }
    for (int i = 0 ;i < n ; i++)
    {
      
    }

}
// Tạo 1 Vecter từ 2 điểm
Vector CreatVecterAB(PointP A, PointP B) { return Vector{ B.x - A.x, B.y - A.y, B.z - A.z }; }

// Chếch 1 điểm thuộc 1 đường thẳng AB
bool CheckCNamTrenAB(PointP Point1, PointP Point2, PointP Point3, double Invalid)
{
    
    double GocGiua2Vecter = Angle2Vector(CreatVecterAB(Point1, Point3), CreatVecterAB(Point2, Point3));
    if (abs(GocGiua2Vecter) <= 0.001 or abs(GocGiua2Vecter - 180) <= 0.001)
    {
        return true;
    }
    return false;
}

//Tính chiều dài 2 đường thẳng nối 2 điểm trong không gian
double DistancePointAB(PointP A, PointP B) { return sqrt(pow((A.x - B.x), 2) + pow((A.y - B.y), 2) + pow((A.z - B.z), 2)); }

// Check 1 điểm nằm trong đường thẳng AB
bool NamTrongAB_Mid(PointP A, PointP B, PointP C, double Invalid)
{
    if (abs(DistancePointAB(A, B) - DistancePointAB(A, C) - DistancePointAB(B, C)) <= Invalid and CheckCNamTrenAB(A, B, C, Invalid) == true) { return true; }
    return false;
}
// Check 1 điểm nằm ngoài đường thẳng AB về phía điểm A
bool NamNgoaiAB_Left(PointP A, PointP B, PointP C, double Invalid)
{
    if (abs(DistancePointAB(B, C) - DistancePointAB(A, C) - DistancePointAB(A, B)) <= Invalid and CheckCNamTrenAB(A, B, C, Invalid) == true) { return true; }
    return false;
}
// Check 1 điểm nằm ngoài đường thẳng AB về phía điểm B
bool NamNgoaiAB_Right(PointP A, PointP B, PointP C, double Invalid)
{
    if (abs(DistancePointAB(A, C) - DistancePointAB(B, C) - DistancePointAB(B, A)) <= Invalid and CheckCNamTrenAB(A, B, C, Invalid) == true) { return true; }
    return false;
}
//check 1 điểm có thuộc đường thằng AB hay không
bool checkpoint_in_AB(PointP A, PointP B, PointP C)
{
    Vector AB; Vector AC;
    AB = CreatVecterAB(A,B);
    AC = CreatVecterAB(A,C);
    double q = Angle2Vector(AB, AC);

    if ( (q < 0.0000001) && (q >179.999) && (q < 180.1) )
    {
        return true;
    }
    else
    {
        return false;
    }

}
//Check 2 điểm trùng nhau
bool ComparePointAB(PointP A, PointP B, double Invalid) { if (abs(A.x - B.x) <= Invalid and abs(A.y - B.y) <= Invalid and abs(A.z - B.z) <= Invalid) { return true; } else { return false; } }

double GocGiua2DuongThang(PointP A, PointP B, PointP C, PointP D)
{
    return Angle2Vector(CreatVecterAB(A, B), CreatVecterAB(C, D));
}

//xác định giao điểm 2 đường thẳng
PointP GiaoDiemABCD(PointP A, PointP B, PointP C, PointP D)
{
    Vector AB = CreatVecterAB(A, B);
    Vector CD = CreatVecterAB(C, D);
    PointP Point;
    if (abs(Angle2Vector(AB, CD)) < 0.1 or abs(Angle2Vector(AB, CD) - 180) < 0.1)
    {
        Point.exist = false;
        return Point;
    }
    else
    {
        double t;
        if (abs(CD.y * AB.x - CD.x * AB.y) > 0.0001)
        {
            t = (C.x * CD.y - C.y * CD.x + A.y * CD.x - A.x * CD.y) / (AB.x * CD.y - AB.y * CD.x);
        }
        else if (abs(AB.x * CD.z - AB.z * CD.x) > 0.0001)
        {
            t = (CD.z * C.x + CD.x * A.z - CD.x * C.z - CD.z * A.x) / (AB.x * CD.z - AB.z * CD.x);
        }
        else
        {
            t = (CD.z * C.y + CD.y * A.z - CD.y * C.z - CD.z * A.y) / (AB.y * CD.z - AB.z * CD.y);
        }
        return PointP{ A.x + AB.x * t,A.y + AB.y * t ,A.z + AB.z * t , true, C.stt };
    }
}

//Tích có hướng 2 vecter
Vector TichCoHuong2VecTor(Vector AB, Vector AC)
{
    return Vector{ AB.y * AC.z - AC.y * AB.z,-(AB.x * AC.z - AC.x * AB.z),AB.x * AC.y - AC.x * AB.y };
}

//Phương trình mặt phẳng đi qua 3 điểm
MatPhang MatPhangABC(PointP A, PointP B, PointP C)
{
    Vector ABAC = TichCoHuong2VecTor(CreatVecterAB(A, B), CreatVecterAB(A, C));
    for (double i = 2; i <= 1000; i++)
    {
        double n1 = fmod(ABAC.x, i);
        double n2 = fmod(ABAC.y, i);
        double n3 = fmod(ABAC.z, i);
        if ((n1 == 0) && (n2 == 0) && (n3 == 0))
        {
            ABAC.x = ABAC.x / i;
            ABAC.y = ABAC.y / i;
            ABAC.z = ABAC.z / i;
        }
    }
    return MatPhang{ ABAC.x,ABAC.y ,ABAC.z,-ABAC.x * A.x - ABAC.y * A.y - ABAC.z * A.z };
}

//Phương trình mặt phẳng đi qua 2 điểm và vuông góc với mặt phẳng cho trước
MatPhang MPPhapTuyenABC(PointP A, PointP B, PointP C)
{
    MatPhang ABC = MatPhangABC(A, B, C);
    Vector nABC = { ABC.a,ABC.b,ABC.c };
    Vector ABnABC = TichCoHuong2VecTor(CreatVecterAB(A, B), nABC);
    for (double i = 2; i <= 1000; i++)
    {
        double n1 = fmod(ABnABC.x, i);
        double n2 = fmod(ABnABC.y, i);
        double n3 = fmod(ABnABC.z, i);
        if ((n1 == 0) && (n2 == 0) && (n3 == 0))
        {
            ABnABC.x = ABnABC.x / i;
            ABnABC.y = ABnABC.y / i;
            ABnABC.z = ABnABC.z / i;
        }
    }
    return MatPhang{ ABnABC.x,ABnABC.y ,ABnABC.z,-ABnABC.x * A.x - ABnABC.y * A.y - ABnABC.z * A.z };
}

// Tìm giao điểm 1 đường thẳng và 1 mặt phẳng
PointP planandline(PointP A, PointP B, MatPhang P)
{
    Vector AB = CreatVecterAB(A, B);
    if (((AB.x * P.a) + (AB.y * P.b) + (AB.z * P.c)) < 0.0001)
    {
        PointP Point1;
        Point1.exist = false;
        return Point1;
    }
    double t = (double)(-P.d - (P.a * A.x) - (P.b * A.y) - (P.c * A.z)) / ((AB.x * P.a) + (AB.y * P.b) + (AB.z * P.c));
    return PointP{ A.x + AB.x * t,A.y + AB.y * t ,A.z + AB.z * t ,true,0 };
}


struct SumPoint
{
public:
    int nPointP;
    std::vector<PointP> PointN;
    bool Type; //Check opening Góc
};

struct AllOpening
{
public:
    std::vector<SumPoint> SPoint;
    int NOpening;
};

struct PointBaoObject
{
public:
    std::vector<PointP> PointN;
    int nPoint;
};


// Tính tích của 1 Point với 1 mặt phẳng
double TichMPVaDiem(MatPhang ABC, PointP A)
{
    return ABC.a * A.x + ABC.b * A.y + ABC.c * A.z + ABC.d;
}

// Xác định 2 point cùng phía với mặt phẳng
bool XDPointCungPhia(MatPhang ABC, PointP A, PointP B)
{
    if (TichMPVaDiem(ABC, A) * TichMPVaDiem(ABC, B) >= 0)
    {
        return true;
    }
    return false;
}



PointP GetPoint3(PointP* Arr, int n, PointP Point1, PointP Point2)
{
    for (int i = 0; i <= n; i++)
    {
        if (ComparePointAB(Point1, Arr[i], 1) == false and ComparePointAB(Point2, Arr[i], 1) == false and CheckCNamTrenAB(Point1, Point2, Arr[i], 1) == false)
        {
            return Arr[i];
        }
    }
}


struct PointGoc
{
public:
    PointP Point;
    bool Check;
};

SumPoint PointBien(PointP* Arr, int n)
{
    PointP Point1, Point2, Point3;
    SumPoint SumPo;
    int sl1 = 0;
    bool Check;
    sl1 = 0;
    for (int i = 0; i < n; i++)
    {
        Point1 = Arr[i]; Point2 = Arr[i + 1];
        Point3 = GetPoint3(Arr, n, Point1, Point2);
        Check = true;
        MatPhang MpPhapTuyen = MPPhapTuyenABC(Point1, Point2, Point3);
        for (int j = 0; j < n; j++)
        {
            if (XDPointCungPhia(MpPhapTuyen, Point3, Arr[j]) == false)
            {
                Check = false; break;
            }
        }
        if (Check == true)
        {
            SumPo.PointN.push_back(Point1);
            SumPo.PointN.push_back(Point2);
            sl1 += 2;
        }
    }
    SumPo.nPointP = sl1;
    return SumPo;
}

//__________________________________________________________________________________________________________________________________________________________________

PointBaoObject GetBaoObject(SumPoint Arr)
{
    PointBaoObject GetRec;
    PointP Point1, Point2, Point3, Point4, PointDau1, PointDau2;
    double GocQuay;
    int k = 0;
    for (int i = 0; i < Arr.nPointP; i += 2)
    {
        Point1 = Arr.PointN[i]; Point2 = Arr.PointN[i + 1];
        for (int j = i + 2; j < Arr.nPointP; j += 2)
        {
            Point3 = Arr.PointN[j]; Point4 = Arr.PointN[j + 1];
            GocQuay = GocGiua2DuongThang(Point1, Point2, Point3, Point4);
            if (abs(GocQuay) > 0.0001 and abs(GocQuay - 180) > 0.0001)
            {
                GetRec.PointN.push_back(GiaoDiemABCD(Point1, Point2, Point3, Point4));
                k += 1;
                if (k == 1)
                {
                    PointDau1 = Point1; PointDau2 = Point2;
                }
                Point1 = Point3; Point2 = Point4;
            }
        }
        GocQuay = GocGiua2DuongThang(PointDau1, PointDau2, Point3, Point4);
        if (abs(GocQuay) > 0.0001 and abs(GocQuay - 180) > 0.0001)
            GetRec.PointN.push_back(GiaoDiemABCD(PointDau1, PointDau2, Point3, Point4));
        k += 1;
        break;
    }
    GetRec.nPoint = k;
    return GetRec;
}

//__________________________________________________________________________________________________________________________________________________________________


//PointP* PointPTG = new PointP[100];

AllOpening GetOpening(PointBaoObject GetRec, SumPoint SumPointBien, PointP* Arr, int n)
{
    AllOpening Allopen;
    PointP* Arr2 = new PointP[n * 2 - 1];
    int k = 0;
    for (int j = 0; j < 2; j++)
    {
        for (int i = 0; i <= n; i++)
        {
            if (!(j == 1 and i == 0) and !(j == 1 and i == n))
            {
                Arr2[k] = Arr[i];
                k += 1;
            }
        }
    }

    SumPoint SumP;
    PointP Point1, Point2, GD;
    bool CheckGD, CheckTrung;

    int Dem, Dem1;
    Dem = Dem1 = 0;
    for (int i = 0; i < SumPointBien.nPointP - 1; i++)
    {
        Dem1 = 0;
        if (SumPointBien.PointN[i + 1].stt - SumPointBien.PointN[i].stt != 1 and SumPointBien.PointN[i + 1].stt - SumPointBien.PointN[i].stt != 0)
        {
            Point1 = Arr2[SumPointBien.PointN[i].stt];
            Point2 = Arr2[SumPointBien.PointN[i + 1].stt];
            CheckGD = false;
            for (int j = 0; j < GetRec.nPoint; j++)
            {
                CheckTrung = false;
                for (int k = 0; k <= n; k++)
                {
                    if (ComparePointAB(GetRec.PointN[j], Arr[k], 1) == true)
                    {
                        CheckTrung = true;
                        break;
                    }
                }
                if (ComparePointAB(GetRec.PointN[j], Point1, 1) == false and ComparePointAB(GetRec.PointN[j], Point2, 1) == false and CheckTrung == false)
                {
                    if (GetRec.PointN[j].stt == Point1.stt or GetRec.PointN[j].stt == Point2.stt)
                    {
                        CheckGD = true;
                        GD = GetRec.PointN[j];
                        break;
                    }
                }
            }

            if (CheckGD == true)
            {
                SumP.PointN.push_back(GD);
                SumP.Type = true;
                Dem1 += 1;
            }
            else
            {
                SumP.Type = false;
            }

            for (int j = SumPointBien.PointN[i].stt; j < SumPointBien.PointN[i + 1].stt + 1; j++)
            {
                PointP Pointp = Arr2[j];
                SumP.PointN.push_back(Pointp);
                Dem1 += 1;
            }
            SumP.nPointP = Dem1;
            Allopen.SPoint.push_back(SumP);
            SumP.PointN.clear();
            Dem++;
        }
    }

    Dem1 = 0;
    SumP.PointN.clear();

    if (SumPointBien.PointN[0].stt != 0 and SumPointBien.PointN[SumPointBien.nPointP - 1].stt != n)
    {
        Point1 = Arr2[SumPointBien.PointN[0].stt];
        Point2 = Arr2[SumPointBien.PointN[SumPointBien.nPointP - 1].stt];

        CheckGD = false;
        for (int j = 0; j < GetRec.nPoint; j++)
        {
            if (ComparePointAB(GetRec.PointN[j], Point1, 1) == false and ComparePointAB(GetRec.PointN[j], Point2, 1) == false)
            {
                if (GetRec.PointN[j].stt == Point1.stt or GetRec.PointN[j].stt == Point2.stt)
                {
                    CheckGD = true;
                    GD = GetRec.PointN[j];
                    break;
                }
            }
        }

        if (CheckGD == true)
        {
            SumP.PointN.push_back(GD);
            Allopen.SPoint[Dem].Type = true;
            Dem1 += 1;
        }
        else
        {
            Allopen.SPoint[Dem].Type = true;
        }

        for (int i = 0; i < n * 2 - 1; i++)
        {
            if (Arr2[i].stt == SumPointBien.PointN[SumPointBien.nPointP - 1].stt)
            {
                for (int j = i; j < n * 2 - 1; j++)
                {
                    SumP.PointN.push_back(Arr2[j]);
                    Dem1 += 1;
                    if (Arr2[j].stt == SumPointBien.PointN[0].stt)
                        break;
                }
            }
        }
        SumP.nPointP = Dem1;
        Allopen.SPoint.push_back(SumP);
        Dem += 1;
    }
    Allopen.NOpening = Dem;
    return Allopen;
}


//PointP* InputArr(int n)
//{
//    PointP* Arr = new PointP[n + 1];
//    Arr[0].x = 1; Arr[0].y = 4; Arr[0].z = 0; Arr[0].stt = 0;
//    Arr[1].x = 2; Arr[1].y = 4; Arr[1].z = 0; Arr[1].stt = 1;
//    Arr[2].x = 2; Arr[2].y = 3; Arr[2].z = 0; Arr[2].stt = 2;
//    Arr[3].x = 3; Arr[3].y = 3; Arr[3].z = 0; Arr[3].stt = 3;
//    Arr[4].x = 3; Arr[4].y = 2; Arr[4].z = 0; Arr[4].stt = 4;
//    Arr[5].x = 6; Arr[5].y = 2; Arr[5].z = 0; Arr[5].stt = 5;
//    Arr[6].x = 6; Arr[6].y = 3; Arr[6].z = 0; Arr[6].stt = 6;
//    Arr[7].x = 7; Arr[7].y = 3; Arr[7].z = 0; Arr[7].stt = 7;
//    Arr[8].x = 7; Arr[8].y = 2; Arr[8].z = 0; Arr[8].stt = 8;
//    Arr[9].x = 8; Arr[9].y = 2; Arr[9].z = 0; Arr[9].stt = 9;
//    Arr[10].x = 8; Arr[10].y = 3; Arr[10].z = 0; Arr[10].stt = 10;
//    Arr[11].x = 9; Arr[11].y = 3; Arr[11].z = 0; Arr[11].stt = 11;
//    Arr[12].x = 9; Arr[12].y = 4; Arr[12].z = 0; Arr[12].stt = 12;
//    Arr[13].x = 10; Arr[13].y = 4; Arr[13].z = 0; Arr[13].stt = 13;
//    Arr[14].x = 10; Arr[14].y = 5; Arr[14].z = 0; Arr[14].stt = 14;
//    Arr[15].x = 11; Arr[15].y = 5; Arr[15].z = 0; Arr[15].stt = 15;
//    Arr[16].x = 11; Arr[16].y = 7; Arr[16].z = 0; Arr[16].stt = 16;
//    Arr[17].x = 10; Arr[17].y = 7; Arr[17].z = 0; Arr[17].stt = 17;
//    Arr[18].x = 10; Arr[18].y = 8; Arr[18].z = 0; Arr[18].stt = 18;
//    Arr[19].x = 11; Arr[19].y = 8; Arr[19].z = 0; Arr[19].stt = 19;
//    Arr[20].x = 11; Arr[20].y = 10; Arr[20].z = 0; Arr[20].stt = 20;
//    Arr[21].x = 10; Arr[21].y = 10; Arr[21].z = 0; Arr[21].stt = 21;
//    Arr[22].x = 10; Arr[22].y = 11; Arr[22].z = 0; Arr[22].stt = 22;
//    Arr[23].x = 9; Arr[23].y = 11; Arr[23].z = 0; Arr[23].stt = 23;
//    Arr[24].x = 9; Arr[24].y = 12; Arr[24].z = 0; Arr[24].stt = 24;
//    Arr[25].x = 7; Arr[25].y = 12; Arr[25].z = 0; Arr[25].stt = 25;
//    Arr[26].x = 7; Arr[26].y = 11; Arr[26].z = 0; Arr[26].stt = 26;
//    Arr[27].x = 6; Arr[27].y = 11; Arr[27].z = 0; Arr[27].stt = 27;
//    Arr[28].x = 6; Arr[28].y = 12; Arr[28].z = 0; Arr[28].stt = 28;
//    Arr[29].x = 4; Arr[29].y = 12; Arr[29].z = 0; Arr[29].stt = 29;
//    Arr[30].x = 4; Arr[30].y = 11; Arr[30].z = 0; Arr[30].stt = 30;
//    Arr[31].x = 3; Arr[31].y = 11; Arr[31].z = 0; Arr[31].stt = 31;
//    Arr[32].x = 3; Arr[32].y = 12; Arr[32].z = 0; Arr[32].stt = 32;
//    Arr[33].x = 1; Arr[33].y = 12; Arr[33].z = 0; Arr[33].stt = 33;
//    Arr[34].x = 1; Arr[34].y = 4; Arr[34].z = 0; Arr[34].stt = 34;
//    for (int i = 0; i <= n; i++)
//    {
//        Arr[i].x = Arr[i].x * 1000;
//        Arr[i].y = Arr[i].y * 1000;
//        Arr[i].z = Arr[i].z * 1000;
//    }
//    return Arr;
//}

//}#pragma once
#pragma once




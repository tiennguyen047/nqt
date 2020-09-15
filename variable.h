#include <iostream>
#include<math.h>
#include <vector>
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
        double t = (C.x * CD.y - C.y * CD.x + A.y * CD.x - A.x * CD.y) / (AB.x * CD.y - AB.y * CD.x);
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
    return MatPhang{ ABAC.x,ABAC.y ,ABAC.z,-ABAC.x * A.x - ABAC.y * A.y - ABAC.z * A.z };
}

//Phương trình mặt phẳng đi qua 2 điểm và vuông góc với mặt phẳng cho trước
MatPhang MPPhapTuyenABC(PointP A, PointP B, PointP C)
{
    MatPhang ABC = MatPhangABC(A, B, C);
    Vector nABC = { ABC.a,ABC.b,ABC.c };
    Vector ABnABC = TichCoHuong2VecTor(CreatVecterAB(A, B), nABC);
    return MatPhang{ ABnABC.x,ABnABC.y ,ABnABC.z,-ABnABC.x * A.x - ABnABC.y * A.y - ABnABC.z * A.z };
}

// Tìm giao điểm 1 đường thẳng và 1 mặt phẳng
PointP planandline(PointP A, PointP B, MatPhang P)
{
    Vector AB = CreatVecterAB(A, B);
    if (((AB.x * P.a) + (AB.y * P.b) + (AB.z * P.c)) < 0.0000001)
    {
        PointP Point1;
        Point1.exist = false;
        return Point1;
    }
    double t = (double)(-P.d - (P.a * A.x) - (P.b * A.y) - (P.c * A.z)) / ((AB.x * P.a) + (AB.y * P.b) + (AB.z * P.c));
    return PointP{ A.x + AB.x * t,A.y + AB.y * t ,A.z + AB.z * t ,true,0 };
}

//#pragma once

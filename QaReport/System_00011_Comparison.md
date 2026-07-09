# SQL Mapper Comparison: admin_system_00011 vs hq_system_00011

This document compares the logic and SQL queries between the Admin and HQ versions of the Web Service Event Log Inquiry.

## 1. Core Logic Differences

The main difference between the two screens is the **data access scope** based on the user's role:

- **Admin (`admin_system_00011`)**: A system-wide administrator who can view **all web service event logs** across all chains and stores in the entire system.
- **HQ (`hq_system_00011`)**: A chain headquarters user who can only view **web service event logs of stores and users belonging to their own chain**.

---

## 2. SQL Query Comparison

### 2.1 `getTotalCnt` (Total Count Query)

| File | Query |
| :--- | :--- |
| **Admin** | `SELECT COUNT(1) FROM hmsfns.SRVLOGTB SR LEFT OUTER JOIN hmsfns.MUSERSTB MU ON SR.USER_ID = MU.USER_ID LEFT OUTER JOIN hmsfns.MMEMBSTB MB ON MU.MS_NO = MB.MS_NO WHERE 1=1 ...` |
| **HQ** | `SELECT COUNT(1) FROM hmsfns.SRVLOGTB SR LEFT OUTER JOIN hmsfns.MUSERSTB MU ON SR.USER_ID = MU.USER_ID LEFT OUTER JOIN hmsfns.MMEMBSTB MB ON MU.MS_NO = MB.MS_NO WHERE MB.CHAIN_NO = #{chainNo} ...` |

> 🔍 **Key Difference**: HQ query contains the constraint `WHERE MB.CHAIN_NO = #{chainNo}` to restrict log counting to the user's chain.

---

### 2.2 `searchServiceLogList` (Log Search Query)

#### Admin Mapper (`Admin_System_00011_Sql.xml`)
```xml
SELECT A.*
  FROM ( SELECT ROW_NUMBER() OVER(ORDER BY SR.LOG_SEQ) RNUM
               , ROW_NUMBER() OVER(ORDER BY SR.LOG_SEQ DESC) ROW_NO
               , SR.LOG_SEQ
               , SR.USER_ID
               , MU.USER_NM
               , SR.REMOTE_IP
               , SR.SERVICE_MENU
               , SR.SERVICE_NAME
               , SR.SERVICE_TYPE
               , TO_CHAR(TO_DATE(SR.CREATE_DTIME, 'YYYYMMDDHH24MISS'), 'YYYY-MM-DD') CREATE_DATE
               , TO_CHAR(TO_DATE(SR.CREATE_DTIME, 'YYYYMMDDHH24MISS'), 'HH24:MI:SS') CREATE_TIME
            FROM hmsfns.SRVLOGTB SR
 LEFT OUTER JOIN hmsfns.MUSERSTB MU ON SR.USER_ID = MU.USER_ID
 LEFT OUTER JOIN hmsfns.MMEMBSTB MB ON MU.MS_NO = MB.MS_NO
           WHERE 1=1
         /* Search conditions (searchFromDate, searchEndDate, userId, userIp) */
       ) A
 WHERE A.ROW_NO >= #{startCount}  AND A.ROW_NO <= #{endCount}
 ORDER BY A.ROW_NO ASC
```

#### HQ Mapper (`Hq_System_00011_Sql.xml`)
```xml
SELECT A.*
  FROM ( SELECT ROW_NUMBER() OVER(ORDER BY SR.LOG_SEQ) RNUM
               , ROW_NUMBER() OVER(ORDER BY SR.LOG_SEQ DESC) ROW_NO
               , SR.LOG_SEQ
               , SR.USER_ID
               , MU.USER_NM
               , SR.REMOTE_IP
               , SR.SERVICE_MENU
               , SR.SERVICE_NAME
               , SR.SERVICE_TYPE
               , TO_CHAR(TO_DATE(SR.CREATE_DTIME, 'YYYYMMDDHH24MISS'), 'YYYY-MM-DD') CREATE_DATE
               , TO_CHAR(TO_DATE(SR.CREATE_DTIME, 'YYYYMMDDHH24MISS'), 'HH24:MI:SS') CREATE_TIME
            FROM hmsfns.SRVLOGTB SR
 LEFT OUTER JOIN hmsfns.MUSERSTB MU ON SR.USER_ID = MU.USER_ID
 LEFT OUTER JOIN hmsfns.MMEMBSTB MB ON MU.MS_NO = MB.MS_NO
           WHERE MB.CHAIN_NO = #{chainNo}
         /* Search conditions (searchFromDate, searchEndDate, userId, userIp) */
       ) A
 WHERE A.ROW_NO >= #{startCount}  AND A.ROW_NO <= #{endCount}
 ORDER BY A.ROW_NO ASC
```

> 🔍 **Key Difference**: HQ query contains `WHERE MB.CHAIN_NO = #{chainNo}` to restrict log lists to the user's chain.


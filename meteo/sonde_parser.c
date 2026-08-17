#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>


/* ============================================================
 * Helpers
 * ============================================================ */

static char *trim(char *s)
{
    char *end;

    while (*s && isspace((unsigned char)*s))
        s++;

    if (*s == '\0')
        return s;

    end = s + strlen(s) - 1;

    while (end > s && isspace((unsigned char)*end))
        end--;

    *(end + 1) = '\0';

    return s;
}


/*
 * Split:
 *
 * 2023/02/13: 15h54m10s: armoire: 22.375
 *
 * into 4 fields.
 */
static int split4(char *line, char **fields)
{
    int n = 0;
    char *p = line;

    fields[n++] = p;

    while (*p && n < 4) {

        if (*p == ':') {

            *p = '\0';
            p++;

            fields[n++] = p;
        }
        else {
            p++;
        }
    }

    if (n < 4)
        return 0;

    fields[0] = trim(fields[0]);
    fields[1] = trim(fields[1]);
    fields[2] = trim(fields[2]);
    fields[3] = trim(fields[3]);

    return 1;
}


/*
 * Check whether string starts with something looking like:
 *
 * YYYY/MM/DD
 */
static int is_office_format(const char *s)
{
    if (!s)
        return 0;

    return (
        isdigit((unsigned char)s[0]) &&
        isdigit((unsigned char)s[1]) &&
        isdigit((unsigned char)s[2]) &&
        isdigit((unsigned char)s[3]) &&
        s[4] == '/'
    );
}


/*
 * Convert epoch to local time.

 * IMPORTANT:
 * This uses the OS timezone.
 *
 * If getCurrentTimeZoneName() in your Python code represents
 * another timezone, we will need to adapt this part.
 */
static int epoch_to_date(
    double epoch,
    int *year,
    int *month,
    int *day,
    int *hour,
    int *minute
)
{
    time_t t;
    struct tm tmv;

    t = (time_t)epoch;

#if defined(_WIN32)

    if (localtime_s(&tmv, &t) != 0)
        return 0;

#else

    if (localtime_r(&t, &tmv) == NULL)
        return 0;

#endif

    *year   = tmv.tm_year + 1900;
    *month  = tmv.tm_mon + 1;
    *day    = tmv.tm_mday;
    *hour   = tmv.tm_hour;
    *minute = tmv.tm_min;

    return 1;
}


/*
 * Create:
 *
 * [year, month, day, hour, minute, value]
 */
static PyObject *create_value(
    int year,
    int month,
    int day,
    int hour,
    int minute,
    double value
)
{
    PyObject *list;

    list = PyList_New(6);

    if (!list)
        return NULL;

    PyList_SET_ITEM(list, 0, PyInt_FromLong(year));
    PyList_SET_ITEM(list, 1, PyInt_FromLong(month));
    PyList_SET_ITEM(list, 2, PyInt_FromLong(day));
    PyList_SET_ITEM(list, 3, PyInt_FromLong(hour));
    PyList_SET_ITEM(list, 4, PyInt_FromLong(minute));
    PyList_SET_ITEM(list, 5, PyFloat_FromDouble(value));

    return list;
}


/* ============================================================
 * Python 2 / Python 3 compatibility
 * ============================================================ */

#if PY_MAJOR_VERSION >= 3

#define PyInt_FromLong PyLong_FromLong

static PyObject *make_string(const char *s)
{
    return PyUnicode_FromString(s);
}

#else

static PyObject *make_string(const char *s)
{
    return PyString_FromString(s);
}

#endif


/* ============================================================
 * Main parser
 * ============================================================ */

static PyObject *
sonde_decode_file(PyObject *self, PyObject *args)
{
    const char *filename;

    FILE *f;

    char line[8192];

    PyObject *allDatas;

    long nNumLine = 0;


    if (!PyArg_ParseTuple(args, "s:decode_file_sonde", &filename))
        return NULL;


    f = fopen(filename, "rb");

    if (!f) {

        PyErr_SetFromErrnoWithFilename(
            PyExc_IOError,
            filename
        );

        return NULL;
    }


    allDatas = PyDict_New();

    if (!allDatas) {

        fclose(f);
        return NULL;
    }


    while (fgets(line, sizeof(line), f) != NULL) {

        char *fields[4];

        char *strDate;
        char *strTime;
        char *strHost;
        char *strMesureName;
        char *strValue;

        int year;
        int month;
        int day;
        int hour;
        int minute;

        double value;

        PyObject *key;
        PyObject *values;
        PyObject *item;


        if (line[0] == '\0')
            continue;


        /*
         * Split line.
         */

        if (!split4(line, fields))
            continue;


        /*
         * --------------------------------------------------------
         * OFFICE SONDE
         * --------------------------------------------------------
         */

        if (is_office_format(fields[0])) {

            strDate = fields[0];
            strTime = fields[1];

            strHost = (char *)"rpi";
            strMesureName = (char *)"Temperature";

            /*
             * Location
             */
            strHost = fields[2];

            /*
             * For office format the original code uses:
             *
             * (location, "temp")
             */

            strValue = fields[3];


            /*
             * Date:
             *
             * YYYY/MM/DD
             */

            if (strlen(strDate) < 10)
                continue;

            year =
                (strDate[0] - '0') * 1000 +
                (strDate[1] - '0') * 100 +
                (strDate[2] - '0') * 10 +
                (strDate[3] - '0');

            month =
                (strDate[5] - '0') * 10 +
                (strDate[6] - '0');

            day =
                (strDate[8] - '0') * 10 +
                (strDate[9] - '0');


            /*
             * Time:
             *
             * HHhMMmSSs
             */

            if (strlen(strTime) < 5)
                continue;

            hour =
                (strTime[0] - '0') * 10 +
                (strTime[1] - '0');

            minute =
                (strTime[3] - '0') * 10 +
                (strTime[4] - '0');


            value = atof(strValue);


            /*
             * key = (location, "temp")
             */

            key = PyTuple_New(2);

            if (!key)
                goto error;

            PyTuple_SET_ITEM(
                key,
                0,
                make_string(strHost)
            );

            PyTuple_SET_ITEM(
                key,
                1,
                make_string("temp")
            );
        }


        /*
         * --------------------------------------------------------
         * WEBSAVE
         * --------------------------------------------------------
         */

        else {

            double epoch;

            epoch = atof(fields[0]);

            strHost = fields[1];
            strMesureName = fields[2];
            strValue = fields[3];


            if (strValue[0] == '\0')
                continue;

            if (strcmp(strValue, "None") == 0)
                continue;


            /*
             * Historical:
             *
             * %22
             */

            {
                char *p = strstr(strValue, "%22");

                if (p) {

                    char *src;
                    char *dst;

                    src = p + 3;
                    dst = p;

                    while (*src) {
                        *dst++ = *src++;
                    }

                    *dst = '\0';
                }
            }


            /*
             * Epoch -> local date/time.
             */

            if (!epoch_to_date(
                epoch,
                &year,
                &month,
                &day,
                &hour,
                &minute
            )) {
                continue;
            }


            value = atof(strValue);


            /*
             * key = (host, measurement)
             */

            key = PyTuple_New(2);

            if (!key)
                goto error;

            PyTuple_SET_ITEM(
                key,
                0,
                make_string(strHost)
            );

            PyTuple_SET_ITEM(
                key,
                1,
                make_string(strMesureName)
            );
        }


        /*
         * --------------------------------------------------------
         * FILTERS
         * --------------------------------------------------------
         */

        if (value < -100.0 || value > 50000.0) {

            Py_DECREF(key);
            continue;
        }


        /*
         * Temperature 85 initialization value.
         */

        if (strstr(strMesureName, "Temp") != NULL) {

            if (value > 84.99 && value < 85.01) {

                Py_DECREF(key);
                continue;
            }
        }
        else {

            if (value < 1.0) {

                Py_DECREF(key);
                continue;
            }
        }


        /*
         * Remove Test.
         */

        if (strstr(strMesureName, "Test") != NULL) {

            Py_DECREF(key);
            continue;
        }


        /*
         * Remove misbb.
         */

        {
            const char *p = strHost;
            int isMisbb = 0;

            while (*p) {

                char c = *p;

                if (c >= 'A' && c <= 'Z')
                    c += 'a' - 'A';

                if (c == 'm') {

                    if (
                        p[0] &&
                        p[1] &&
                        p[2] &&
                        p[3] &&
                        p[4]
                    ) {

                        if (
                            c == 'm' &&
                            p[1] == 'i' &&
                            p[2] == 's' &&
                            p[3] == 'b' &&
                            p[4] == 'b'
                        ) {
                            isMisbb = 1;
                            break;
                        }
                    }
                }

                p++;
            }

            if (isMisbb) {

                Py_DECREF(key);
                continue;
            }
        }


        /*
         * --------------------------------------------------------
         * APPEND
         * --------------------------------------------------------
         */

        values = PyDict_GetItem(allDatas, key);

        if (values == NULL) {

            values = PyList_New(0);

            if (!values) {

                Py_DECREF(key);
                goto error;
            }

            if (PyDict_SetItem(
                allDatas,
                key,
                values
            ) < 0) {

                Py_DECREF(values);
                Py_DECREF(key);

                goto error;
            }

            Py_DECREF(values);
        }


        item = create_value(
            year,
            month,
            day,
            hour,
            minute,
            value
        );

        if (!item) {

            Py_DECREF(key);
            goto error;
        }


        if (PyList_Append(values, item) < 0) {

            Py_DECREF(item);
            Py_DECREF(key);

            goto error;
        }


        Py_DECREF(item);
        Py_DECREF(key);

        nNumLine++;
    }


    fclose(f);

    return allDatas;


error:

    fclose(f);

    Py_DECREF(allDatas);

    return NULL;
}


/* ============================================================
 * Python module
 * ============================================================ */

static PyMethodDef SondeMethods[] = {

    {
        "decode_file_sonde",
        sonde_decode_file,
        METH_VARARGS,
        "Decode a sonde/websave file."
    },

    {NULL, NULL, 0, NULL}
};


#if PY_MAJOR_VERSION >= 3

static struct PyModuleDef sondeModule = {

    PyModuleDef_HEAD_INIT,

    "sonde_parser",

    "Fast sonde file parser",

    -1,

    SondeMethods
};


PyMODINIT_FUNC
PyInit_sonde_parser(void)
{
    return PyModule_Create(&sondeModule);
}

#else

PyMODINIT_FUNC
initsonde_parser(void)
{
    Py_InitModule(
        "sonde_parser",
        SondeMethods
    );
}

#endif
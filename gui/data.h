#pragma once

#include <QtCore>
#include <QtXml>

class Data
{
public:
	Data();
	~Data();

	int dimension() { return _dim; }
	int nstep() { return _nstep; }

	double getTime(int istep) { return _ts[istep]; }
	double getStartingTime() { return _ts[0]; }
	double getEndingTime() { return _ts[_nstep - 1]; }
	double getValue(int istep, int idim);
	double getTarget(int istep, int idim);

	void clear();

	void loadFromDom(QDomElement &element);
	void saveToDom(QDomDocument &doc, QDomElement &parent);

private:
	int _dim, _nstep;
	double *_ts;
	QMap<int, double *> _xs, _rs;
	QMap<int, double> _kps, _kis, _kds;

	QString _mckFormula, _targetFormula;
};
#include "data.h"

QString changeArrayIntoString(double *xs, int n)
{
	QStringList strs;
	for (int i = 0; i < n; i++)
		strs << QString("%1").arg(xs[i]);
	return strs.join(",");
}

//=============================================================================

Data::Data()
{
	_dim = 0;
	_nstep = 0;
	_ts = NULL;
}

Data::~Data()
{
	clear();
}

double Data::getValue(int istep, int idim)
{
	double *xs = _xs.value(idim, NULL);
	return xs ? xs[istep] : 0;
}

double Data::getTarget(int istep, int idim)
{
	double *rs = _rs.value(idim, NULL);
	return rs ? rs[istep] : 0;
}

void Data::clear()
{
	_dim = 0;
	if (_ts)
		delete[] _ts;
	_ts = NULL;

	QMapIterator<int, double *> iter_x(_xs);
	while (iter_x.hasNext()) {
		iter_x.next();
		delete[] iter_x.value();
	}
	_xs.clear();

	QMapIterator<int, double *> iter_r(_rs);
	while (iter_r.hasNext()) {
		iter_r.next();
		delete[] iter_r.value();
	}
	_rs.clear();

	_kps.clear();
	_kis.clear();
	_kds.clear();

	_mckFormula.clear();
	_targetFormula.clear();
}

void Data::loadFromDom(QDomElement &element)
{
	QStringList strs_ts = element.firstChildElement("time-series").text().split(",");

	_nstep = strs_ts.size();
	_ts = new double[_nstep];
	for (int istep = 0; istep < _nstep; istep++)
		_ts[istep] = strs_ts.at(istep).toDouble();

	QDomElement dimensionElement = element.firstChildElement("dimension");
	while (!dimensionElement.isNull())
	{
		int idim = dimensionElement.attribute("id").toInt() - 1;
		QStringList strs_xs = dimensionElement.firstChildElement("series").text().split(",");
		QStringList strs_rs = dimensionElement.firstChildElement("target").text().split(",");

		double *xs = new double[_nstep];
		double *rs = new double[_nstep];

		for (int istep = 0; istep < _nstep; istep++) {
			xs[istep] = (istep < strs_xs.size()) ? strs_xs.at(istep).toDouble() : strs_xs.last().toDouble();
			rs[istep] = (istep < strs_rs.size()) ? strs_rs.at(istep).toDouble() : strs_rs.last().toDouble();
		}

		_xs[idim] = xs;
		_rs[idim] = rs;
		
		dimensionElement = dimensionElement.nextSiblingElement("dimension");
	}

	_dim = _xs.count();
}

void Data::saveToDom(QDomDocument &doc, QDomElement &parent)
{
	QDomElement element = doc.createElement("time-series");
	element.appendChild(doc.createTextNode(changeArrayIntoString(_ts, _nstep)));
	parent.appendChild(element);

	for (int idim = 0; idim < _dim; idim++)
	{
		QDomElement dimensionElement = doc.createElement("dimension");
		dimensionElement.setAttribute("id", idim + 1);

		QDomElement seriesElement = doc.createElement("series");
		QDomElement targetElement = doc.createElement("target");
		seriesElement.appendChild(doc.createTextNode(changeArrayIntoString(_xs.value(idim), _nstep)));
		targetElement.appendChild(doc.createTextNode(changeArrayIntoString(_rs.value(idim), _nstep)));

		dimensionElement.appendChild(seriesElement);
		dimensionElement.appendChild(targetElement);
		parent.appendChild(dimensionElement);
	}

}
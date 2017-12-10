#include "sysview.h"

SysView::SysView(QWidget *parent)
	: QWidget(parent)
{
	mckEdit = new QTextEdit(this);
	noiseEdit = new QTextEdit(this);

	QLabel *mckLabel = new QLabel("def calcMCK(t, x, dx)", this);
	QLabel *noiseLabel = new QLabel("def noise(ndim)", this);

	QVBoxLayout *layout = new QVBoxLayout;
	layout->setMargin(0);
	layout->setSpacing(0);
	layout->addWidget(mckLabel);
	layout->addWidget(mckEdit);
	layout->addWidget(noiseLabel);
	layout->addWidget(noiseEdit);

	setLayout(layout);
}
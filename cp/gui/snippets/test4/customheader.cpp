#include "customheader.h"
#include <QLayout>
#include <QPushButton>

CustomHeader::CustomHeader(QWidget *parent) :
    QWidget(parent)
{
    QHBoxLayout *l = new QHBoxLayout(this);

}

void CustomHeader::addSection(const QString &txt) {
    QPushButton *pb = new QPushButton;
    pb->setText(txt);
    QHBoxLayout *l = (QHBoxLayout*)layout();
    l->addWidget(pb);
}

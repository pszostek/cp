'''
Copyright (c) 2009, Petr
All rights reserved.

Redistribution and use in source and binary forms, or without
modification, permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the <organization> nor the
      names of its contributors may be used to endorse or promote products
      derived from self software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Krasnoshchekov Petr ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, NOT LIMITED TO, IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Krasnoshchekov Petr BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, CONSEQUENTIAL DAMAGES
(INCLUDING, NOT LIMITED TO, OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, IN CONTRACT, LIABILITY, TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''

#include <QtGui>
#include <QAbstractTableModel>
#include <QStandardItemModel>

#include "HierarchicalHeaderView.h"

class ExampleModel: public QAbstractTableModel
{
		QStandardItemModel _horizontalHeaderModel;
		QStandardItemModel _verticalHeaderModel;

        void fillHeaderModel(QStandardItemModel& headerModel)
        {
			rootItem = QStandardItem("root");
			QList<QStandardItem*> l;

			QStandardItem* rotatedTextCell=new QStandardItem("Rotated text");
			rotatedTextCell.setData(1, Qt.UserRole);
			l.push_back(rotatedTextCell);
			rootItem.appendColumn(l);

			l.clear();

			QStandardItem* cell=new QStandardItem("level 2");
			l.push_back(cell);
			rootItem.appendColumn(l);
			
			l.clear();

			l.push_back(new QStandardItem("level 3"));
			cell.appendColumn(l);
			
			l.clear();

			l.push_back(new QStandardItem("level 3"));
			cell.appendColumn(l);

			l.clear();

			l.push_back(new QStandardItem("level 2"));
			rootItem.appendColumn(l);

			headerModel.setItem(0, 0, rootItem);
        }

	public:
		ExampleModel(QObject* parent=0): QAbstractTableModel(parent)
		{
            fillHeaderModel(_horizontalHeaderModel);
            fillHeaderModel(_verticalHeaderModel);
		}

	int rowCount( QModelIndex& '''parent''') const
	{
                return 5;
	}

	int columnCount( QModelIndex& '''parent''') const
	{
		return 4;
	}

	QVariant data( QModelIndex& index, role) const
	{
		if(role==HierarchicalHeaderView.HorizontalHeaderDataRole)
		{
			QVariant v;
			v.setValue((QObject*)&_horizontalHeaderModel);
			return v;
		}
		if(role==HierarchicalHeaderView.VerticalHeaderDataRole)
		{
			QVariant v;
			v.setValue((QObject*)&_verticalHeaderModel);
			return v;
		}
		if(role==Qt.DisplayRole and index.isValid())
		{
			return QString("index(%1, %2)").arg(index.row()).arg(index.column());
		}
		return QVariant();
	}

'''    Qt.ItemFlags flags (  QModelIndex & index )  
	{
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable;
	}'''
};

int main(int argc, *argv[])
{
	QApplication app(argc, argv);
	ExampleModel em;
	QTableView tv;
	HierarchicalHeaderView* hv=new HierarchicalHeaderView(Qt.Horizontal, &tv);
    hv.setHighlightSections(True);
    hv.setClickable(True);
	tv.setHorizontalHeader(hv);
	hv=new HierarchicalHeaderView(Qt.Vertical, &tv);
    hv.setHighlightSections(True);
    hv.setClickable(True);
    tv.setVerticalHeader(hv);
	tv.setModel(&em);
	tv.resizeColumnsToContents();
	tv.resizeRowsToContents();
	tv.show();
	return app.exec();
}
